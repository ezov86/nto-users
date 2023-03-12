from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class EmailAuthEntry(Base):
    """
    Entry that stores data for user to authenticate with name/email and password.
    Password can be changed with email if this option is not disabled for user.
    Necessity of email verification depends on config.
    Used by EmailAuthStrategy.
    """

    __tablename__ = "email_auth"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(primary_key=True, index=True, unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    password_updated_with_token: Mapped[str] = mapped_column(nullable=True, default=None)
    can_update_password: Mapped[bool] = mapped_column(nullable=False, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)

    user = relationship("User", lazy="joined")
