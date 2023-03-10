from fastapi import Depends

from app.config import get_config, Config
from app.core.crypto import decode_jwt, InvalidJWTError
from app.core.models import User, TelegramAuthEntry
from app.core.register import RegistrationService
from app.core.repos import TelegramAuthRepo, UserRepo
from app.core.security import UserIsNotPermittedError
from .base import AuthStrategy, LoginCredentials, AddStrategyData, InvalidAuthDataError


class TelegramAddStrategyData(AddStrategyData):
    # 'name' inherited.
    token: str


class TelegramLoginCredentials(LoginCredentials):
    # 'scopes' inherited.
    token: str


class TelegramAuthStrategy(AuthStrategy[TelegramLoginCredentials, TelegramAddStrategyData]):
    """
    Authentication via telegram requires only valid Telegram JWT generated on the service side.
    """
    def __init__(
            self,
            tg_auth_repo: TelegramAuthRepo = Depends(),
            user_repo: UserRepo = Depends(),
            config: Config = Depends(get_config),
            reg: RegistrationService = Depends()
    ):
        self.tg_auth_repo = tg_auth_repo
        self.user_repo = user_repo
        self.config = config
        self.reg = reg

    def _get_sub_from_token(self, token: str) -> str:
        try:
            payload = decode_jwt(token, [], self.config.telegram.token_secret)
        except InvalidJWTError:
            raise InvalidAuthDataError()

        return str(payload["sub"])

    def add_to_user(self, user: User, data: TelegramAddStrategyData):
        # Raises InvalidAuthDataError.
        tg_user_id = self._get_sub_from_token(data.token)

        # Add new strategy.
        # Raises NotUniqueError.
        self.tg_auth_repo.create(TelegramAuthEntry(
            tg_user_id=tg_user_id,
            user=user
        ))

    def login_for_user_model_or_fail(self, schema: TelegramLoginCredentials) -> User:
        # Raises InvalidAuthDataError.
        tg_user_id = self._get_sub_from_token(schema.token)

        # Find auth entry.
        if (tg_auth_entry := self.tg_auth_repo.get_by_tg_user_id(tg_user_id)) is None:
            raise InvalidAuthDataError()

        # Check user is permitted to authenticate.
        if tg_auth_entry.user.is_disabled:
            raise UserIsNotPermittedError()

        return tg_auth_entry.user
