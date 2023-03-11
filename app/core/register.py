from datetime import datetime

from fastapi import Depends

from app.config import Config, get_config
from app.core.models import User
from app.core.repos import UserRepo, ModelNotUniqueError
from app.core.strategies import AuthStrategy
from app.core.strategies import AddStrategyDataType


class UserAlreadyExistsError(Exception):
    def __init__(self, msg="User already exists"):
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
        """
        Register user using given auth strategy.
        Auth data will be attached to created user.

        :param strategy: auth strategy.
        :param auth_data: data for auth strategy.

        :raises UserAlreadyExistsError: user with given name already exists.
        :raises InvalidAuthDataError: invalid auth data.

        :return: created user.
        """

        user_for_db = User(
            name=auth_data.name,
            is_disabled=False,
            scopes=self.config.user_default.scopes,
            registered_at=datetime.utcnow()
        )

        try:
            # Will also add to DB user in one commit.
            # Raises InvalidAuthDataError.
            strategy.add_to_user(user_for_db, auth_data)
        except ModelNotUniqueError:
            raise UserAlreadyExistsError()

        return self.user_repo.create(user_for_db)
