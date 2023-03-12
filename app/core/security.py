"""
Security helpers for authentication/authorization process.
"""

from dataclasses import dataclass

from app.core import exc
from app.core.models import User


def get_valid_scopes(requested_scopes: list[str], user: User) -> list[str]:
    """
    Get valid scopes from the requested ones.

    :param requested_scopes: scopes that was requested.
    :param user: a user.

    :return: list of available scopes based on the requested ones.
    """

    # Admin has full access.
    if "admin" in user.scopes:
        return requested_scopes

    # User is requesting all available scopes.
    if "all" in requested_scopes:
        return user.scopes

    # Extract only available scopes from the requested.
    available_from_requested = []
    for scope in requested_scopes:
        if scope in user.scopes:
            available_from_requested.append(scope)

    return available_from_requested


def check_scopes_valid(scopes: list[str], user: User):
    """
    Checks that requested scopes are valid for given user.

    :raises AccessDeniedError
    """

    if "admin" in user.scopes:
        return

    for scope in scopes:
        if scope not in user.scopes:
            raise exc.AccessDenied(f"requested scope {scope}")


def check_user_not_disabled(user: User):
    """
    Check that user is not disabled.

    :raises AccessDenied: user is disabled.
    """

    if user.is_disabled:
        raise exc.AccessDenied("disabled user")


@dataclass(frozen=True, kw_only=True)
class AuthenticatedUser:
    name: str
    scopes: list[str]
    user: User

    def is_admin(self) -> bool:
        return "admin" in self.scopes

    def is_permitted(self, scopes: list[str]) -> bool:
        if self.is_admin():
            return True

        for scope in scopes:
            if scope not in self.scopes:
                return False

        return True

    def authorize(self, scopes: list[str]):
        if self.is_permitted(scopes):
            raise exc.AccessDenied(f"action that requires scopes {', '.join(scopes)}")


@dataclass(frozen=True, kw_only=True)
class AuthorizedUser(AuthenticatedUser):
    """
    Same as authenticated user.
    """
