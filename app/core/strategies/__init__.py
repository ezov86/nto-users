from .base import (
    InvalidCredentialsError,
    StrategyAlreadyAttachedError,
    UserIsNotPermittedError,
    LoginCredentialsType,
    RegisterCredentialsType,
    AddStrategyCredentialsType,
    AuthStrategy
)
from .telegram import (
    TelegramRegisterCredentials,
    TelegramAddStrategyCredentials,
    TelegramLoginCredentials,
    TelegramAuthStrategy
)
