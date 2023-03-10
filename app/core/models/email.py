from sqlalchemy import Column, String, Integer, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from .base import Base


class EmailAuthEntry(Base):
    """
    Entry that stores data for user to authenticate with name/email and password.
    Password can be changed with email if this option is not disabled for user.
    Necessity of email verification depends on config.
    Used by EmailAuthStrategy.
    """

    __tablename__ = "email_auth"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    password_updated_with_token = Column(String, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    user = relationship("User")
