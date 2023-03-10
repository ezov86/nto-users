from fastapi import Depends
from sqlalchemy.orm import Session

from .base import BaseRepo, ModelNotFoundError

from app.db import get_session
from app.core.models import User


class UserRepo(BaseRepo[User]):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session, User)

    def get_by_name(self, name: str) -> User | None:
        # noinspection PyTypeChecker
        return self.session.query(User).where(
            User.name == name
        ).first()

    def get_by_name_or_fail(self, name: str) -> User:
        """
        :raises ModelNotFoundError: if user not found.

        :return: found user model.
        """

        if (user := self.get_by_name(name)) is None:
            raise ModelNotFoundError("User not found.")

        return user
