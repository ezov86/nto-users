from .base import (
    InvalidCredentialsError,
    StrategyAlreadyAttachedError,
    UserIsNotPermittedError,
    LoginSchemaType,
    RegisterSchemaType,
    AddStrategySchemaType,
    AuthStrategy
)
from .telegram import (
    TelegramRegisterSchema,
    TelegramAddStrategySchema,
    TelegramLoginSchema,
    TelegramAuthStrategy
)
