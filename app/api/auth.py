from typing import Callable

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core import exc
from app.core.auth_tokens import AuthTokensService
from app.core.security import AuthenticatedUser, AuthorizedUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/tg/login")


async def get_authenticated_user(
        access_token: str = Depends(oauth2_scheme),
        auth_service: AuthTokensService = Depends()
) -> AuthenticatedUser:
    """
    For use by endpoints as a dependency.
    Returns only authenticated user.

    :raises HTTPException: 401 - invalid JWT.
    """

    try:
        return await auth_service.get_auth_user_from_access_token(access_token)
    except (exc.InvalidAuthData, exc.AccessDenied) as e:
        raise HTTPException(401, str(e))


def get_authorized_user(scopes: list[str] = None) -> Callable:
    """
    For use by endpoints as wrapper in dependencies.
    Wrapped function returns authorized with requested scopes user.

    :raises HTTPException: (from wrapped function) 403 - access is denied for requested scopes.
    """

    if scopes is None:
        scopes = []

    def wrapped_func(auth_user: AuthenticatedUser = Depends(get_authenticated_user)) -> AuthorizedUser:
        if not auth_user.is_permitted(scopes):
            raise HTTPException(403, "User is not permitted")

        return AuthorizedUser(
            name=auth_user.name,
            scopes=auth_user.scopes,
            user=auth_user.user
        )

    return wrapped_func
