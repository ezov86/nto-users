from dataclasses import dataclass

from fastapi import Depends
from pydantic import BaseModel, ValidationError

from app.config import get_config, Config
from app.core import exc
from app.core.crypto import decode_jwt
from app.core.models import User, TelegramAccount
from app.core.repos import TelegramAccountRepo
from .base import AuthStrategy, Credentials, AddAuthAccountData


@dataclass(frozen=True, kw_only=True)
class TelegramAddAccountData(AddAuthAccountData):
    token: str


@dataclass(frozen=True, kw_only=True)
class TelegramCredentials(Credentials):
    token: str


class TelegramTokenDataSchema(BaseModel):
    tg_user_id: str
    tg_username: str
    tg_first_name: str
    tg_last_name: str | None
    tg_photo_url: str | None


class TelegramAuthStrategy(AuthStrategy[TelegramCredentials, TelegramAddAccountData, TelegramAccount]):
    """
    Authentication via telegram requires only valid Telegram JWT generated by nto-tg-jwt.
    """

    def __init__(self,
                 tg_account_repo: TelegramAccountRepo = Depends(),
                 config: Config = Depends(get_config)
                 ):
        self.tg_account_repo = tg_account_repo
        self.config = config

    def _decode_tg_token(self, token: str) -> TelegramTokenDataSchema:
        try:
            payload = decode_jwt(token, [
                "tg_username",
                "tg_first_name",
                "tg_last_name",
                "tg_photo_url"
            ], self.config.telegram.token_secret)

            # Rename "sub" to "tg_user_id".
            payload["tg_user_id"] = payload["sub"]
            del payload["sub"]

            return TelegramTokenDataSchema(**payload)
        except (exc.InvalidToken, ValidationError):
            raise exc.InvalidAuthData()

    def add_auth_account_to_user(self, user: User, data: TelegramAddAccountData) -> User:
        # Raises InvalidAuthData.
        token_account_date = self._decode_tg_token(data.token)

        user.telegram_account = TelegramAccount(
            **token_account_date.__dict__,
            user=user
        )

        return user

    async def login_for_user(self, schema: TelegramCredentials) -> User:
        # Raises InvalidAuthData.
        token_account_data = self._decode_tg_token(schema.token)

        # Find auth data in db.
        account = await self.tg_account_repo.get_by_tg_user_id(token_account_data.tg_user_id)
        if account is None:
            raise exc.InvalidAuthData()

        # Token data is ok, update profile data.
        account.update_fields(**token_account_data.__dict__)
        account = await self.tg_account_repo.update(account)

        return account.user
