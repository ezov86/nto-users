from dataclasses import dataclass

from pydantic import EmailStr

from app.core.models import User
from app.core.models.email import EmailAuthEntry
from .base import AddAuthMethodData, AuthStrategy, LoginCredentials


@dataclass(frozen=True, kw_only=True)
class EmailAddAuthMethodData(AddAuthMethodData):
    # 'name' inherited.
    email: str
    password: str
    verified: bool


@dataclass(frozen=True, kw_only=True)
class EmailLoginCredentials(LoginCredentials):
    """
    Put EmailStr value into 'name_or_email' if email given, else str.
    """
    # 'scopes' inherited.
    name_or_email: str | EmailStr
    password: str


class EmailAuthStrategy(AuthStrategy[EmailLoginCredentials, EmailAddAuthMethodData, EmailAuthEntry]):
    """
    Authentication via email requires a valid email address and password.
    Email address should be verified if EmailAddStrategyData.verified=False was given.
    Password can be updated via email.
    """
    def add_auth_method_to_user(self, user: User, data: EmailAddAuthMethodData):
        pass

    def login_for_user_model_or_fail(self, credentials: EmailLoginCredentials) -> User:
        pass
