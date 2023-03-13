from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class EmailAccount(Base):
    """
    Data for user to authenticate with name/email and password.
    """

    __tablename__ = "email_auth"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(primary_key=True, index=True, unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    password_updated_with_token: Mapped[str] = mapped_column(nullable=True, default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)

    user = relationship("User", back_populates="email_account", lazy="joined")
