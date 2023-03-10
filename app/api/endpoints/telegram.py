from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.schemas import username_constr, UserSchema, AuthTokensSchema
from app.core.auth import AuthenticationService
from app.core.security import UserIsNotPermittedError
from app.core.strategies import TelegramAuthStrategy, InvalidAuthDataError, TelegramLoginCredentials, \
    TelegramAddStrategyData
from app.core.register import UserAlreadyExistsError, RegistrationService

tg_router = APIRouter(
    tags=["telegram"]
)


class TelegramRegisterSchema(BaseModel):
    name: username_constr
    token: str


@tg_router.post(
    path="/tg/register",
    status_code=201,
    description="Register a new user with telegram token",
    responses={
        400: {"description": "Invalid authentication data. "
                             "Or user is already exists"}
    }
)
def tg_register(
        body: TelegramRegisterSchema,
        reg_service: RegistrationService = Depends(),
        auth_strategy: TelegramAuthStrategy = Depends(),
) -> UserSchema:
    try:
        user_from_db = reg_service.register(
            auth_strategy,
            TelegramAddStrategyData(
                name=body.name,
                token=body.token
            )
        )
    except (InvalidAuthDataError, UserAlreadyExistsError) as e:
        raise HTTPException(400, str(e))

    return UserSchema(
        id=user_from_db.id,
        name=user_from_db.name,
        is_disabled=user_from_db.is_disabled,
        scopes=user_from_db.scopes,
        registered_at=user_from_db.registered_at
    )


class TelegramLoginSchema(BaseModel):
    token: str
    scope: str


@tg_router.post(
    path="/tg/login",
    status_code=200,
    description="Login with telegram token",
    responses={
        400: {"description": "Invalid authentication data"},
        403: {"description": "User is not permitted to authorize"}
    }
)
def tg_login(
        body: TelegramLoginSchema,
        auth_service: AuthenticationService = Depends(),
        auth_strategy: TelegramAuthStrategy = Depends()
) -> AuthTokensSchema:
    auth_service.set_strategy(auth_strategy)
    try:
        tokens = auth_service.login_for_tokens(TelegramLoginCredentials(
            token=body.token,
            scopes=body.scope.split()
        ))
    except InvalidAuthDataError as e:
        raise HTTPException(400, str(e))
    except UserIsNotPermittedError as e:
        raise HTTPException(403, str(e))

    return AuthTokensSchema(
        access=tokens.access,
        refresh=tokens.refresh
    )
