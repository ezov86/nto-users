from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.schemas import username_constr, UserSchema
from app.core.auth_strategies import TelegramRegisterSchema, TelegramAuthStrategy, InvalidCredentialsError
from app.core.register import UserAlreadyExistsError

tg_router = APIRouter(
    tags=["telegram"]
)


class TelegramRegisterValidatedSchema(BaseModel):
    name: username_constr
    token: str


@tg_router.post(
    path="/tg/register",
    status_code=201,
    responses={
        400: {"description": "Invalid credentials given. "
                             "Or user associated with given credentials already exists."}
    }
)
def tg_register(
        body: TelegramRegisterValidatedSchema,
        auth_strategy: TelegramAuthStrategy = Depends(),
) -> UserSchema:
    try:
        user_from_db = auth_strategy.register(TelegramRegisterSchema(
            name=body.name,
            token=body.token
        ))
    except (InvalidCredentialsError, UserAlreadyExistsError) as e:
        raise HTTPException(400, str(e))

    return UserSchema(
        id=user_from_db.id,
        name=user_from_db.name,
        is_disabled=user_from_db.is_disabled,
        scopes=user_from_db.scopes,
        registered_at=user_from_db.registered_at
    )
