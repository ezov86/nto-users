from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import TelegramAuthData
from app.core.models.base import Base
from app.core.models.types import ScopesArrayType


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    is_disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    scopes: Mapped[list[str]] = mapped_column(ScopesArrayType, nullable=False, default=[])
    registered_at: Mapped[datetime] = mapped_column(nullable=False)

    telegram_auth: Mapped["TelegramAuthData"] = relationship(back_populates="user", lazy="joined")
