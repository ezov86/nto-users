from sqlalchemy import Column, String, Boolean, DateTime, Integer

from app.core.models.base import Base
from app.core.models.types import ScopesArrayType


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)
    scopes = Column(ScopesArrayType, nullable=False, default=[])
    registered_at = Column(DateTime, nullable=False)
