from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.auth import get_authorized_user
from app.api.schemas import username_constr, UserSchema, AuthTokensSchema
from app.core import exc
from app.core.auth_tokens import AuthTokensService
from app.core.register import RegistrationService
from app.core.security import AuthorizedUser
from app.core.auth_strategies import TelegramAuthStrategy, TelegramLoginCredentials, TelegramAddAccountData

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
async def tg_register(
        body: TelegramRegisterSchema,
        reg_service: RegistrationService = Depends(),
        auth_strategy: TelegramAuthStrategy = Depends()
) -> UserSchema:
    try:
        user_from_db = await reg_service.register(
            auth_strategy,
            TelegramAddAccountData(
                name=body.name,
                token=body.token
            )
        )
    except (exc.InvalidAuthData, exc.AlreadyExists) as e:
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
async def tg_login(
        body: TelegramLoginSchema,
        auth_service: AuthTokensService = Depends(),
        auth_strategy: TelegramAuthStrategy = Depends()
) -> AuthTokensSchema:
    try:
        tokens = await auth_service.login_for_tokens(auth_strategy, TelegramLoginCredentials(
            token=body.token,
            scopes=body.scope.split()
        ))
    except exc.InvalidAuthData as e:
        raise HTTPException(400, str(e))
    except exc.AccessDenied as e:
        raise HTTPException(403, str(e))

    return AuthTokensSchema(
        access=tokens.access,
        refresh=tokens.refresh
    )


class TelegramAddStrategySchema(BaseModel):
    token: str


@tg_router.post(
    path="/tg/add",
    status_code=204,
    description="Add Telegram authentication to user's account. Requires scope",
    responses={
        400: {"description": "Invalid auth data. Or Telegram user is already attached"}
    }
)
async def tg_add_to_user(
        body: TelegramAddStrategySchema,
        auth_user: AuthorizedUser = Depends(get_authorized_user()),
        auth_strategy: TelegramAuthStrategy = Depends()
):
    try:
        await auth_strategy.add_auth_account_to_user(auth_user.user, TelegramAddAccountData(
            name=auth_user.name,
            token=body.token
        ))
    except exc.InvalidAuthData as e:
        raise HTTPException(400, str(e))
    except exc.AlreadyExists:
        raise HTTPException(400, "Telegram user already attached")


class TelegramAccountSchema(BaseModel):
    tg_user_id: str
    tg_username: str
    tg_first_name: str
    tg_last_name: str | None
    tg_photo_url: str | None


@tg_router.get(
    path="/tg/account",
    status_code=200,
    description="Get Telegram auth account for authorized user. If no Telegram account attached, null is returned"
)
async def tg_get_account(
        auth_user: AuthorizedUser = Depends(get_authorized_user()),
        auth_strategy: TelegramAuthStrategy = Depends()
) -> TelegramAccountSchema | None:
    data = await auth_strategy.get_auth_method_data(auth_user.user)

    if data is None:
        return None
    else:
        return TelegramAccountSchema(
            tg_user_id=data.tg_user_id,
            tg_username=data.tg_username,
            tg_first_name=data.tg_username,
            tg_last_name=data.tg_last_name,
            tg_photo_url=data.tg_photo_url
        )
