from .base import (
    InvalidCredentialsError,
    StrategyAlreadyAttachedError,
    UserIsNotPermittedError
)
from .telegram import (
    TelegramRegisterSchema,
    TelegramAddStrategySchema,
    TelegramLoginSchema,
    TelegramAuthStrategy
)
