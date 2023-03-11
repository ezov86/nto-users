from abc import abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic

from app.core.models import User


class InvalidAuthDataError(Exception):
    def __init__(self, msg="Invalid authentication data"):
        super().__init__(msg)


class StrategyAlreadyAttachedError(Exception):
    def __init__(self, msg="User already has this auth strategy"):
        super().__init__(msg)


@dataclass(frozen=True, kw_only=True)
class AddStrategyData:
    name: str


@dataclass(frozen=True, kw_only=True)
class LoginCredentials:
    scopes: list[str]


LoginCredentialsType = TypeVar("LoginCredentialsType", bound=LoginCredentials)
AddStrategyDataType = TypeVar("AddStrategyDataType", bound=AddStrategyData)


class AuthStrategy(Generic[LoginCredentialsType, AddStrategyDataType]):
    """
    Authentication strategy implements the way of user is authenticated.
    It also implements the way user can add needed auth data.
    """

    @abstractmethod
    def add_to_user(self, user: User, data: AddStrategyDataType):
        """
        Add new authentication strategy to existing/new user's account.

        :param user: user model, if was not added to db, then method will add it.
        :param data: data.

        :raises InvalidAuthDataError: invalid data.
        :raises repos.ModelNotUniqueError: auth data is not unique.
        """

    @abstractmethod
    def login_for_user_model_or_fail(self, credentials: LoginCredentialsType) -> User:
        """
        Verify given credentials for login and return associated user model or fail.

        :raises InvalidAuthDataError: credentials are invalid.
        :raises UserIsNotPermittedError: user is not permitted to authorize.
        """
