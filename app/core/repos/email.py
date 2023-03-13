from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exc
from app.core.models.email import EmailAccount
from app.core.repos import BaseRepo
from app.db import get_session


class EmailAccountRepo(BaseRepo[EmailAccount]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session, EmailAccount)

    async def get_by_email(self, email: str) -> EmailAccount | None:
        result = await self.session.execute(
            select(EmailAccount).where(EmailAccount.email == email)
        )
        # noinspection PyTypeChecker
        return result.one()

    async def get_by_email_or_fail(self, email: str) -> EmailAccount:
        """
        :raises NotFound: account not found.
        """
        if (account := self.get_by_email(email)) is None:
            raise exc.NotFound("Email account")

        return account
