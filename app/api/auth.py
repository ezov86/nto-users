from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import AuthenticationService
from app.core.crypto import InvalidJWTError
from app.core.security import AuthenticatedUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/tg/login")


def get_authenticated_user(
        access_token: str = Depends(oauth2_scheme),
        auth_service: AuthenticationService = Depends()
) -> AuthenticatedUser:
    """
    For use by endpoints as a dependency.
    """

    try:
        return auth_service.get_auth_user_from_access_token(access_token)
    except InvalidJWTError as e:
        raise HTTPException(400, str(e))
