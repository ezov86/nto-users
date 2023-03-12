from abc import abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic

from app.core.models import User, Base


@dataclass(frozen=True, kw_only=True)
class AddAuthMethodData:
    """
    Data required for strategy to add new auth method.
    """
    name: str


@dataclass(frozen=True, kw_only=True)
class LoginCredentials:
    """
    Data required for strategy to login.
    """
    scopes: list[str]


LoginCredentialsType = TypeVar("LoginCredentialsType", bound=LoginCredentials)
AddAuthMethodDataType = TypeVar("AddAuthMethodDataType", bound=AddAuthMethodData)
AuthMethodDataType = TypeVar("AuthMethodDataType", bound=Base)


class AuthStrategy(Generic[LoginCredentialsType, AddAuthMethodDataType, AuthMethodDataType]):
    """
    Authentication strategy implements the way of user is authenticated.
    It also implements the way user can add needed auth data.
    """

    @abstractmethod
    def add_auth_method_to_user(self, user: User, data: AddAuthMethodDataType):
        """
        Attaches new authentication method to given user model.

        :param user: user model.
        :param data: data.

        :raises InvalidAuthData: invalid data.
        """

    @abstractmethod
    async def login_for_user_model_or_fail(self, credentials: LoginCredentialsType) -> User:
        """
        Verify given credentials for login and return associated user model or fail.
        No scopes check is guaranteed.

        :raises InvalidAuthData: credentials are invalid.
        :raises AccessDenied: user is not permitted to authorize.
        """

    @abstractmethod
    async def get_auth_method_data(self, user: User) -> AuthMethodDataType | None:
        """
        Returns auth data used by strategy that is attached to given user or None.
        """
