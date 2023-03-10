from .base import (
    InvalidCredentialsError,
    StrategyAlreadyAttachedError,
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
