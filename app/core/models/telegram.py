from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class TelegramAuthEntry(Base):
    """
    Entry that stores data for user to authenticate via Telegram.
    """

    __tablename__ = "telegram_auth"

    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(String, index=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User")
