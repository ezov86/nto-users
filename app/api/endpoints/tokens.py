from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.api.auth import get_authenticated_user
from app.api.schemas import AuthTokensSchema
from app.core import exc
from app.core.auth_tokens import AuthTokensService
from app.core.security import AuthenticatedUser

tokens_router = APIRouter(
    tags=["tokens"]
)


@tokens_router.post(
    path="/tokens/refresh",
    status_code=200,
    description="Return new access and refresh token",
    responses={
        400: {"description": "Invalid token"},
        403: {"description": "Access denied"}
    }
)
async def refresh_tokens(
        refresh_token: str = Header(),
        auth_service: AuthTokensService = Depends()
) -> AuthTokensSchema:
    try:
        tokens = await auth_service.refresh_tokens(refresh_token)
    except exc.InvalidAuthData as e:
        raise HTTPException(400, str(e))
    except exc.AccessDenied as e:
        raise HTTPException(403, str(e))

    return AuthTokensSchema(
        access=tokens.access,
        refresh=tokens.refresh
    )


class AuthenticatedUserSchema(BaseModel):
    name: str
    scopes: list[str]


@tokens_router.get(
    path="/tokens/user",
    status_code=200,
    description="Return authenticated user data",
    responses={
        400: {"description": "Invalid token"},
    }
)
async def get_user_from_tokens(
        auth_user: AuthenticatedUser = Depends(get_authenticated_user)
) -> AuthenticatedUserSchema:
    return AuthenticatedUserSchema(
        name=auth_user.name,
        scopes=auth_user.scopes
    )
