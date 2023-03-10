from abc import abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel

from app.core.models import User


class InvalidAuthDataError(Exception):
    def __init__(self, msg="Invalid authentication data."):
        super().__init__(msg)


class StrategyAlreadyAttachedError(Exception):
    def __init__(self, msg="Authentication strategy was already attached to the user."):
        super().__init__(msg)


class AddStrategyData(BaseModel):
    name: str


class LoginCredentials(BaseModel):
    scopes: list[str]


LoginCredentialsType = TypeVar("LoginCredentialsType", bound=LoginCredentials)
AddStrategyDataType = TypeVar("AddStrategyDataType", bound=AddStrategyData)


class AuthStrategy(Generic[LoginCredentialsType, AddStrategyDataType]):
    """
    Authentication strategy implements the way of user is authenticated.
    It also implements the way user can add required auth data.
    """

    @abstractmethod
    def check_can_add_to_user_or_fail(self, data: AddStrategyDataType):
        """
        Check that given registration data is valid or fail.
        If this method passes without raises, then it is safe to call register().

        :raises InvalidAuthDataError: invalid data.
        """

    @abstractmethod
    def add_to_user(self, user: User, date: AddStrategyDataType):
        """
        Add new authentication strategy to user's account.

        :raises StrategyAlreadyAttachedError: strategy is already attached to the user.
        :raises InvalidAuthDataError: invalid data.
        """

    @abstractmethod
    def login_for_user_model_or_fail(self, credentials: LoginCredentialsType) -> User:
        """
        Verify given credentials for login and return associated user model or fail.

        :raises InvalidAuthDataError: credentials are invalid.
        :raises UserIsNotPermittedError: user is not permitted to authorize.
        """
