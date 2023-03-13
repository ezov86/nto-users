from fastapi import Depends

from app.config import Config
from app.core import exc
from app.core.crypto import encode_jwt, decode_jwt, hash_password
from app.core.repos import EmailAccountRepo
from app.mail_sender import MailSender


class EmailService:
    def __init__(self,
                 mail_sender: MailSender = Depends(),
                 email_repo: EmailAccountRepo = Depends(),
                 config: Config = Depends()
                 ):
        self.mail_sender = mail_sender
        self.email_repo = email_repo
        self.config = config

    async def request_verify_token(self, email: str):
        """
        Request sending verify token for user to the given email address.

        :raises NotFound: user's email account not found.
        :raises AlreadyDoneNonIdempotentAction: user's email account is already verified.
        """

        account = await self.email_repo.get_by_email_or_fail(email)

        if account.is_verified:
            raise exc.AlreadyDoneNonIdempotentAction("email verification")

        token = encode_jwt(
            account.email,
            self.config.email.verify_token_secret,
            self.config.email.verify_token_expire
        )

        self.mail_sender.send_verification_mail(email, token)

    async def verify_by_token(self, token: str):
        """
        Verify account by token sent by request_verify_token().

        :raises AlreadyDoneNonIdempotentAction: account is already verified.
        :raises InvalidToken: token is invalid.
        """

        # Raises InvalidToken.
        payload = decode_jwt(token, [], self.config.email.verify_token_secret)
        email = payload["sub"]

        if (account := await self.email_repo.get_by_email(email)) is None:
            raise exc.InvalidToken("email verification")

        if account.is_verified:
            raise exc.AlreadyDoneNonIdempotentAction("email verification")

        account.is_verified = True
        await self.email_repo.update(account)

    async def request_password_update_token(self, email: str):
        """
        Request sending password update token for user to the given email address.

        :raises NotFound: user's email account not found.
        """

        account = await self.email_repo.get_by_email_or_fail(email)

        token = encode_jwt(
            account.email,
            self.config.email.pwd_update_token_secret,
            self.config.email.verify_token_expire
        )

        self.mail_sender.send_password_update_mail(account.email, token)

    async def update_password_by_token(self, token: str, new_password: str):
        """
        Update password to the new one with token sent by request_password_update_token().

        :raises AlreadyDoneNonIdempotentAction: this token is already used to update the password.
        :raises InvalidToken: token is invalid.
        """

        payload = decode_jwt(token, [], self.config.email.verify_token_secret)
        email = payload["sub"]

        if (account := await self.email_repo.get_by_email(email)) is None:
            raise exc.InvalidToken("password update")

        if account.password_updated_with_token == token:
            raise exc.AlreadyDoneNonIdempotentAction("password update with given token")

        account.password_hash = hash_password(new_password)
        account.password_updated_with_token = token

        await self.email_repo.update(account)
