from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.email import EmailAccount
from app.core.repos import BaseRepo
from app.db import get_session


class EmailAccountsRepo(BaseRepo[EmailAccount]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session, EmailAccount)

    async def get_by_email(self, email: str) -> EmailAccount:
        result = await self.session.execute(
            select(EmailAccount).where(EmailAccount.email == email)
        )
        # noinspection PyTypeChecker
        return result.one()
