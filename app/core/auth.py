from fastapi import Depends
from pydantic import BaseModel

from app.config import Config, get_config
from app.core.crypto import encode_token, decode_token
from app.core.models import User
from app.core.security import UserIsNotPermittedError, AuthenticatedUserSchema
from app.core.strategies import LoginSchemaType
from app.core.strategies import AuthStrategy


class AuthTokensSchema(BaseModel):
    access: str
    refresh: str


class AuthenticationService:
    strategy: AuthStrategy

    def __init__(
            self,
            config: Config = Depends(get_config)
    ):
        self.config = config

    def set_strategy(self, strategy: AuthStrategy):
        self.strategy = strategy

    def _encode_tokens(self, username: str, scopes: list[str]) -> AuthTokensSchema:
        scopes_str = " ".join(scopes)

        access_token = encode_token(
            username,
            self.config.oauth.access_token_secret,
            self.config.oauth.access_token_expire,
            {"scopes": scopes_str}
        )

        refresh_token = encode_token(
            username,
            self.config.oauth.refresh_token_secret,
            self.config.oauth.refresh_token_expire,
            {"scopes": scopes_str}
        )

        return AuthTokensSchema(
            access=access_token,
            refresh=refresh_token
        )

    def _check_requested_scopes(self, user: User, scopes: list[str]) -> bool:
        if "admin" in user.scopes:
            return True

        for request_scope in scopes:
            if request_scope not in user.scopes:
                return False

    def login_for_tokens(self, credentials: LoginSchemaType) -> AuthTokensSchema:
        """
        Login for access and refresh token.

        :param credentials: credentials for auth strategy.

        :raises InvalidCredentialsError: invalid credentials.
        :raises UserIsNotPermittedError: user is not permitted to authorize.

        :return: access and refresh token.
        """

        # Raises InvalidCredentialsError, UserIsNotPermittedError.
        user = self.strategy.login_for_user_model_or_fail(credentials)

        if not self._check_requested_scopes(user, credentials.scopes):
            raise UserIsNotPermittedError("User is not permitted to login in requested scopes.")

        return self._encode_tokens(user.name, credentials.scopes)

    def get_auth_user_from_access_token(self, access_token: str) -> AuthenticatedUserSchema:
        """
        Get authenticated user from access token.

        :param access_token: access token.

        :raises InvalidTokenError: invalid token.

        :return: authenticated user.
        """

        # Raises InvalidTokenError
        payload = decode_token(
            access_token,
            ["exp", "scopes"],
            self.config.oauth.access_token_secret
        )

        return AuthenticatedUserSchema(
            name=str(payload["sub"]),
            scopes=str(payload["scopes"]).split()
        )

    def refresh_tokens(self, refresh_token: str) -> AuthTokensSchema:
        """
        Get new tokens with refresh-token.

        :param refresh_token: old refresh token.

        :raises InvalidTokenError: invalid token.

        :return: new access and refresh token.
        """

        # Raises InvalidTokenError
        payload = decode_token(
            refresh_token,
            ["exp", "scopes"],
            self.config.oauth.access_token_secret
        )

        return AuthTokensSchema(
            name=str(payload["sub"]),
            scopes=str(payload["scopes"]).split()
        )
