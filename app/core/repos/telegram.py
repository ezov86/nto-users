from fastapi import Depends
from sqlalchemy.orm import Session

from .base import BaseRepo

from app.core.models import TelegramAuthEntry
from app.db import get_session


class TelegramAuthRepo(BaseRepo[TelegramAuthEntry]):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session, TelegramAuthEntry)

    def get_by_tg_user_id(self, tg_user_id: str) -> TelegramAuthEntry:
        # noinspection PyTypeChecker
        return self.session.query(TelegramAuthEntry).where(
            TelegramAuthEntry.tg_user_id == tg_user_id
        ).first()
