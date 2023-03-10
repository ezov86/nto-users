from datetime import datetime

from fastapi import Depends
from pydantic import BaseModel

from app.core.models import User
from app.core.repos import UserRepo


class UserRegisterSchema(BaseModel):
    name: str
    scopes: list[str]


class UserAlreadyExistsError(Exception):
    def __init__(self, msg="User with given credentials already exists."):
        super().__init__(msg)


class RegistrationService:
    """
    Registers new user.
    """
    def __init__(self, user_repo: UserRepo = Depends()):
        self.user_repo = user_repo

    def register(self, user: UserRegisterSchema) -> User:
        if self.user_repo.get_by_name(user.name) is not None:
            raise UserAlreadyExistsError()

        user_for_db = User(
            name=user.name,
            is_disabled=False,
            scopes=user.scopes,
            registered_at=datetime.utcnow()
        )

        return self.user_repo.create(user_for_db)
