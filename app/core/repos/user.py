from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User
from app.core import exc
from app.db import get_session
from .base import BaseRepo


class UserRepo(BaseRepo[User]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session, User)

    async def get_by_name(self, name: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.name == name)
        )

        # noinspection PyTypeChecker
        return result.one()

    async def get_by_name_or_fail(self, name: str) -> User:
        """
        :raises NotFound: if user not found.

        :return: found user model.
        """

        if (user := await self.get_by_name(name)) is None:
            raise exc.NotFound("User")

        return user
