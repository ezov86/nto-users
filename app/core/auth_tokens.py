from dataclasses import dataclass

from fastapi import Depends

from app.config import Config, get_config
from app.core import exc
from app.core.crypto import encode_jwt, decode_jwt
from app.core.models import User
from app.core.repos import UserRepo
from app.core.security import AuthenticatedUser, get_valid_scopes, check_scopes_valid, check_user_not_disabled
from app.core.auth_strategies import AuthStrategy
from app.core.auth_strategies import LoginCredentialsType


@dataclass(frozen=True, kw_only=True)
class AuthTokens:
    access: str
    refresh: str


class AuthTokensService:
    def __init__(self, config: Config = Depends(get_config), user_repo: UserRepo = Depends()):
        self.config = config
        self.user_repo = user_repo

    def _encode_tokens(self, username: str, scopes: list[str]) -> AuthTokens:
        scopes_str = " ".join(scopes)

        access_token = encode_jwt(
            username,
            self.config.oauth.access_token_secret,
            self.config.oauth.access_token_expire,
            {"scopes": scopes_str}
        )

        refresh_token = encode_jwt(
            username,
            self.config.oauth.refresh_token_secret,
            self.config.oauth.refresh_token_expire,
            {"scopes": scopes_str}
        )

        return AuthTokens(
            access=access_token,
            refresh=refresh_token
        )

    async def login_for_tokens(self,
                               strategy: AuthStrategy,
                               credentials: LoginCredentialsType
                               ) -> AuthTokens:
        """
        Login for access and refresh token.

        :param strategy: auth strategy.
        :param credentials: credentials for auth strategy.

        :raises InvalidAuthData: invalid credentials.
        :raises AccessDenied: user is not permitted to authorize.

        :return: access and refresh token.
        """

        # Raises InvalidAuthData.
        user = await strategy.login_for_user(credentials)

        # Raises AccessDenied.
        check_user_not_disabled(user)

        verified_scopes = get_valid_scopes(credentials.scopes, user)

        return self._encode_tokens(user.name, verified_scopes)

    async def _validate_token_payload(self, username: str, scopes: list[str]) -> User:
        if (user := await self.user_repo.get_by_name(username)) is None:
            raise exc.InvalidAuthData()

        # Raises AccessDenied.
        check_user_not_disabled(user)
        check_scopes_valid(scopes, user)

        return user

    async def get_auth_user_from_access_token(self, access_token: str) -> AuthenticatedUser:
        """
        Get authenticated user from access token.

        :param access_token: access token.

        :raises InvalidAuthData: invalid token.
        :raises AccessDenied: user is not permitted to authorize.

        :return: authenticated user.
        """

        try:
            payload = decode_jwt(
                access_token,
                ["exp", "scopes"],
                self.config.oauth.access_token_secret
            )
        except exc.InvalidToken:
            raise exc.InvalidAuthData()

        username = str(payload["sub"])
        scopes = str(payload["scopes"]).split()

        # Raises InvalidAuthData, AccessDenied.
        user = await self._validate_token_payload(username, scopes)

        return AuthenticatedUser(
            name=username,
            scopes=scopes,
            user=user
        )

    async def refresh_tokens(self, refresh_token: str) -> AuthTokens:
        """
        Get new tokens with refresh-token.

        :param refresh_token: old refresh token.

        :raises InvalidAuthData: invalid token.
        :raises AccessDenied: user is not permitted to authorize.

        :return: new access and refresh token.
        """

        # Raises InvalidTokenError
        try:
            payload = decode_jwt(
                refresh_token,
                ["exp", "scopes"],
                self.config.oauth.refresh_token_secret
            )
        except exc.InvalidToken:
            raise exc.InvalidAuthData()

        username = str(payload["sub"])
        scopes = str(payload["scopes"]).split()

        # Raises InvalidAuthData, AccessDenied.
        await self._validate_token_payload(username, scopes)

        return self._encode_tokens(username, scopes)
