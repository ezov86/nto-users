from abc import abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic

from app.core.models import User, Base


@dataclass(frozen=True, kw_only=True)
class AddAuthAccountData:
    """
    Data required for strategy to add new auth method.
    """


@dataclass(frozen=True, kw_only=True)
class Credentials:
    """
    Data required for strategy to login.
    """


LoginCredentialsType = TypeVar("LoginCredentialsType", bound=Credentials)
AddAuthAccountDataType = TypeVar("AddAuthAccountDataType", bound=AddAuthAccountData)
AuthMethodDataType = TypeVar("AuthMethodDataType", bound=Base)


class AuthStrategy(Generic[LoginCredentialsType, AddAuthAccountDataType, AuthMethodDataType]):
    """
    Authentication strategy implements the way of user is authenticated.
    It also implements the way user can add needed data for their auth account.
    """

    @abstractmethod
    def add_auth_account_to_user(self, user: User, data: AddAuthAccountDataType) -> User:
        """
        Attaches new authentication account to given user model.

        :param user: user model.
        :param data: data.

        :raises InvalidAuthData: invalid data.

        :returns: user with new attached account (same as object passed to 'user' param).
        """

    @abstractmethod
    async def login_for_user(self, credentials: LoginCredentialsType) -> User:
        """
        Verify given credentials for login and return associated user model or fail.
        No scopes check is guaranteed.

        :raises InvalidAuthData: credentials are invalid.
        :raises AccessDenied: user is not permitted to authenticate.
        """
