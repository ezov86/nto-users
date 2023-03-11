from dataclasses import dataclass

from app.core.models import User


class UserIsNotPermittedError(Exception):
    def __init__(self, msg="User is not permitted"):
        super().__init__(msg)


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
            raise UserIsNotPermittedError()
