from fastapi import Depends
from pydantic import BaseModel

from app.config import get_config, Config
from app.core.crypto import decode_token, InvalidTokenError
from app.core.models import User, TelegramAuthEntry
from app.core.register import RegistrationService, UserRegisterSchema
from app.core.repos import TelegramAuthRepo, UserRepo
from .base import AuthStrategy, InvalidCredentialsError, UserIsNotPermittedError, LoginSchema, RegisterSchema, \
    AddStrategySchema


class TelegramRegisterSchema(LoginSchema):
    # 'scopes' inherited from LoginSchema.
    name: str
    token: str


class TelegramAddStrategySchema(RegisterSchema):
    name: str
    token: str


class TelegramLoginSchema(AddStrategySchema):
    token: str


class TelegramAuthStrategy(AuthStrategy[TelegramLoginSchema, TelegramRegisterSchema, TelegramAddStrategySchema]):
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
            payload = decode_token(token, [], self.config.telegram.token_secret)
        except InvalidTokenError:
            raise InvalidCredentialsError()

        return str(payload["sub"])

    def register(self, schema: TelegramRegisterSchema) -> User:
        # Raises InvalidCredentialsError.
        tg_user_id = self._get_sub_from_token(schema.token)

        # Check that token is already in db.
        if self.tg_auth_repo.get_by_tg_user_id(tg_user_id) is not None:
            raise InvalidCredentialsError()

        # Raises UserAlreadyExistsError.
        user_from_db = self.reg.register(UserRegisterSchema(
            name=schema.name,
            scopes=self.config.user_default.scopes
        ))

        # Now create auth entry.
        self.tg_auth_repo.create(TelegramAuthEntry(
            tg_user_id=tg_user_id,
            user=user_from_db
        ))

        return user_from_db

    def add_auth_strategy(self, schema: TelegramAddStrategySchema):
        # Find user.
        if (user := self.user_repo.get_by_name(schema.name)) is None:
            raise InvalidCredentialsError()

        # Raises InvalidCredentialsError.
        tg_user_id = self._get_sub_from_token(schema.token)

        # Add new strategy.
        self.tg_auth_repo.create(TelegramAuthEntry(
            tg_user_id=tg_user_id,
            user=user
        ))

    def login_for_user_model_or_fail(self, schema: TelegramLoginSchema) -> User:
        # Raises InvalidCredentialsError.
        tg_user_id = self._get_sub_from_token(schema.token)

        # Find auth entry.
        if (tg_auth_entry := self.tg_auth_repo.get_by_tg_user_id(tg_user_id)) is None:
            raise InvalidCredentialsError()

        # Check user is permitted to authenticate.
        if tg_auth_entry.user.is_disabled:
            raise UserIsNotPermittedError()

        return tg_auth_entry.user
