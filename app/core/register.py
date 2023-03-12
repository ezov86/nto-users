from datetime import datetime

from fastapi import Depends

from app.config import Config, get_config
from app.core.models import User
from app.core.repos import UserRepo
from app.core.auth_strategies import AuthStrategy
from app.core.auth_strategies import AddAuthMethodDataType


class RegistrationService:
    """
    Registers new user.
    """

    def __init__(self, config: Config = Depends(get_config), user_repo: UserRepo = Depends()):
        self.config = config
        self.user_repo = user_repo

    async def register(self, strategy: AuthStrategy, auth_data: AddAuthMethodDataType) -> User:
        """
        Register user using given auth strategy.
        Auth data will be attached to created user.

        :param strategy: auth strategy.
        :param auth_data: data for auth strategy.

        :raises AlreadyExists: user with given name already exists.
        :raises InvalidAuthData: invalid auth data.

        :return: created user.
        """

        user_for_db = User(
            name=auth_data.name,
            is_disabled=False,
            scopes=self.config.user_default.scopes,
            registered_at=datetime.utcnow()
        )

        # Raises InvalidAuthData.
        strategy.add_auth_method_to_user(user_for_db, auth_data)

        # Raises AlreadyExists.
        return await self.user_repo.create(user_for_db)
