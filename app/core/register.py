from datetime import datetime

from fastapi import Depends
from pydantic import BaseModel

from app.config import Config, get_config
from app.core.models import User
from app.core.repos import UserRepo
from app.core.strategies import AuthStrategy
from app.core.strategies import AddStrategyDataType


class UserRegisterSchema(BaseModel):
    name: str
    scopes: list[str]


class UserAlreadyExistsError(Exception):
    def __init__(self, msg="User already exists."):
        super().__init__(msg)


class RegistrationService:
    """
    Registers new user.
    """

    def __init__(
            self,
            user_repo: UserRepo = Depends(),
            config: Config = Depends(get_config)
    ):
        self.user_repo = user_repo
        self.config = config

    def register(self, strategy: AuthStrategy, auth_data: AddStrategyDataType) -> User:
        if self.user_repo.get_by_name(auth_data.name) is not None:
            raise UserAlreadyExistsError()

        strategy.check_can_add_to_user_or_fail(auth_data)

        user_for_db = User(
            name=auth_data.name,
            is_disabled=False,
            scopes=self.config.user_default.scopes,
            registered_at=datetime.utcnow()
        )

        strategy.add_to_user(user_for_db, auth_data)

        return self.user_repo.create(user_for_db)
