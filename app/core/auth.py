from dataclasses import dataclass

from fastapi import Depends

from app.config import Config, get_config
from app.core.crypto import encode_jwt, decode_jwt, InvalidJWTError
from app.core.models import User
from app.core.repos import UserRepo
from app.core.security import UserIsNotPermittedError, AuthenticatedUser, get_valid_scopes, are_scopes_valid
from app.core.strategies import AuthStrategy
from app.core.strategies import LoginCredentialsType


@dataclass(frozen=True, kw_only=True)
class AuthTokens:
    access: str
    refresh: str


class AuthenticationService:
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

    def login_for_tokens(self, strategy: AuthStrategy, credentials: LoginCredentialsType) -> AuthTokens:
        """
        Login for access and refresh token.

        :param strategy: auth strategy.
        :param credentials: credentials for auth strategy.

        :raises InvalidAuthDataError: invalid credentials.
        :raises UserIsNotPermittedError: user is not permitted to authorize.

        :return: access and refresh token.
        """

        # Raises InvalidCredentialsError, UserIsNotPermittedError.
        user = strategy.login_for_user_model_or_fail(credentials)

        verified_scopes = get_valid_scopes(credentials.scopes, user)

        return self._encode_tokens(user.name, verified_scopes)

    def _validate_token_payload(self, username: str, scopes: list[str]) -> User:
        """
        Passes payload is valid or fails.

        :raises InvalidJWTError: user not found.
        :raises UserIsNotPermittedError: user is not permitted in scopes.

        :return: token's owner.
        """

        if (user := self.user_repo.get_by_name(username)) is None:
            raise InvalidJWTError()

        if user.is_disabled:
            raise UserIsNotPermittedError()

        if not are_scopes_valid(scopes, user):
            raise UserIsNotPermittedError()

        return user

    def get_auth_user_from_access_token(self, access_token: str) -> AuthenticatedUser:
        """
        Get authenticated user from access token.

        :param access_token: access token.

        :raises InvalidJWTError: invalid token.
        :raises UserIsNotPermittedError: user is not permitted to authorize.

        :return: authenticated user.
        """

        # Raises InvalidJWTError
        payload = decode_jwt(
            access_token,
            ["exp", "scopes"],
            self.config.oauth.access_token_secret
        )

        username = str(payload["sub"])
        scopes = str(payload["scopes"]).split()

        # Raises InvalidJWTError, UserIsNotPermittedError.
        user = self._validate_token_payload(username, scopes)

        return AuthenticatedUser(
            name=username,
            scopes=scopes,
            user=user
        )

    def refresh_tokens(self, refresh_token: str) -> AuthTokens:
        """
        Get new tokens with refresh-token.

        :param refresh_token: old refresh token.

        :raises InvalidJWTError: invalid token.
        :raises UserIsNotPermittedError: user is not permitted to authorize.

        :return: new access and refresh token.
        """

        # Raises InvalidTokenError
        payload = decode_jwt(
            refresh_token,
            ["exp", "scopes"],
            self.config.oauth.refresh_token_secret
        )

        username = str(payload["sub"])
        scopes = str(payload["scopes"]).split()

        # Raises InvalidJWTError, UserIsNotPermittedError.
        self._validate_token_payload(username, scopes)

        return self._encode_tokens(username, scopes)
