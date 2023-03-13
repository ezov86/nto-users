from dataclasses import dataclass
from typing import assert_never

from fastapi import Depends
from pydantic import EmailStr

from app.core.models import User
from app.core.models.email import EmailAccount
from app.core import exc
from app.core.crypto import hash_password, verify_password
from app.core.repos import EmailAccountsRepo, UserRepo
from app.config import Config, get_config
from .base import AddAuthMethodData, AuthStrategy, LoginCredentials


@dataclass(frozen=True, kw_only=True)
class EmailAddAccountData(AddAuthMethodData):
    # 'name' inherited.
    email: str
    password: str
    is_verified: bool | None
    """ If None then default from config is used. """


@dataclass(frozen=True, kw_only=True)
class EmailLoginCredentials(LoginCredentials):
    name_or_email: str | EmailStr
    """ Put EmailStr value if email given, else str. """
    password: str


class EmailAuthStrategy(AuthStrategy[EmailLoginCredentials, EmailAddAccountData, EmailAccount]):
    """
    Authentication via email requires a valid email address and password.
    Email verification is required EmailAccount.is_verified = False.
    Password can be updated via email.
    """

    def __init__(self,
                 email_repo: EmailAccountsRepo = Depends(),
                 user_repo: UserRepo = Depends(),
                 config: Config = Depends(get_config)
                 ):
        self.email_repo = email_repo
        self.user_repo = user_repo
        self.config = config

    def add_auth_method_to_user(self, user: User, data: EmailAddAccountData):
        if data.is_verified is None:
            is_verified = not self.config.email.should_verify
        else:
            is_verified = data.is_verified

        user.email_auth = EmailAccount(
            email=data.email,
            is_verified=is_verified,
            password_hash=hash_password(data.password),
            password_updated_with_token=None
        )

    async def _get_account(self, name_or_email: str | EmailStr) -> EmailAccount | None:
        if type(name_or_email) == str:
            # Find user.
            user = await self.user_repo.get_by_name(name_or_email)
            if user is None:
                return None  # No user found -> no account found.

            return user.email_auth
        elif type(name_or_email) == EmailStr:
            return await self.email_repo.get_by_email(name_or_email)
        else:
            assert_never(name_or_email)

    async def login_for_user_model_or_fail(self, credentials: EmailLoginCredentials) -> User:
        account = await self._get_account(credentials.name_or_email)
        if account is None:
            raise exc.InvalidAuthData()

        if not verify_password(credentials.password, account.password_hash):
            raise exc.InvalidAuthData()

        return account.user

    async def get_auth_method_data(self, user: User) -> EmailAccount | None:
        return user.email_auth
