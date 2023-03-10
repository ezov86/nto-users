from abc import abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel

from app.core.models import User


class InvalidCredentialsError(Exception):
    def __init__(self, msg="Invalid credentials."):
        super().__init__(msg)


class StrategyAlreadyAttachedError(Exception):
    def __init__(self, msg="Authentication strategy was already attached to the user."):
        super().__init__(msg)


class LoginCredentials(BaseModel):
    scopes: list[str]


class RegisterCredentials(BaseModel):
    pass


class AddStrategyCredentials(BaseModel):
    pass


LoginCredentialsType = TypeVar("LoginCredentialsType", bound=LoginCredentials)
RegisterCredentialsType = TypeVar("RegisterCredentialsType", bound=RegisterCredentials)
AddStrategyCredentialsType = TypeVar("AddStrategyCredentialsType", bound=AddStrategyCredentials)


class AuthStrategy(Generic[LoginCredentialsType, RegisterCredentialsType, AddStrategyCredentialsType]):
    """
    Authentication strategy implements the way user registers their accounts, attaches new strategy for their account
    and uses it to login.

    It may also implement other actions for updating user data that is required for this type of authentication,
    such as password update for strategy that requires password.
    """

    @abstractmethod
    def register(self, schema: RegisterCredentialsType) -> User:
        """
        Register new account with credentials and add new authentication strategy to it.

        :raises InvalidCredentialsError: invalid credentials.
        :raises register.UserAlreadyExistsError: user already exists.

        :return: created user.
        """

    @abstractmethod
    def add_auth_strategy(self, schema: AddStrategyCredentialsType):
        """
        Add new authentication strategy to user's account.

        :raises StrategyAlreadyAttachedError: strategy is already attached to the user.
        :raises InvalidCredentialsError: invalid credentials.
        """

    @abstractmethod
    def login_for_user_model_or_fail(self, schema: LoginCredentialsType) -> User:
        """
        Verify given credentials for login and return associated user model or fail.

        :raises InvalidCredentialsError: credentials are invalid.
        :raises UserIsNotPermittedError: user is not permitted to authorize.
        """
