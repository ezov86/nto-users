from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class TelegramAccount(Base):
    """
    Entry that stores data for user to authenticate via Telegram.
    """

    __tablename__ = "telegram_auth"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tg_user_id: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    tg_username: Mapped[str] = mapped_column(nullable=False)
    tg_first_name: Mapped[str] = mapped_column(nullable=False)
    tg_last_name: Mapped[str | None] = mapped_column(default=None)
    tg_photo_url: Mapped[str | None] = mapped_column(default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User", back_populates="telegram_account", lazy="joined")
