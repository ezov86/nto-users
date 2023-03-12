from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import TelegramAuthData
from app.db import get_session
from .base import BaseRepo


class TelegramAuthRepo(BaseRepo[TelegramAuthData]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session, TelegramAuthData)

    async def get_by_tg_user_id(self, tg_user_id: str) -> TelegramAuthData:
        result = await self.session.execute(
            select(TelegramAuthData).where(TelegramAuthData.tg_user_id == tg_user_id)
        )
        # noinspection PyTypeChecker
        return result.one()
