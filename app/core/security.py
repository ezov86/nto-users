from pydantic import BaseModel


class UserIsNotPermittedError(Exception):
    def __init__(self, msg="User is not permitted"):
        super().__init__(msg)


class AuthenticatedUser(BaseModel):
    name: str
    scopes: list[str]

    def is_admin(self) -> bool:
        return "admin" in self.scopes

    def is_permitted(self, scopes: list[str]) -> bool:
        if self.is_admin():
            return True

        for scope in scopes:
            if scope not in self.scopes:
                return False

        return True
