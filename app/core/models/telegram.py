from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class TelegramAuthEntry(Base):
    """
    Entry that stores data for user to authenticate via Telegram.
    """

    __tablename__ = "telegram_auth"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tg_user_id: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User")
