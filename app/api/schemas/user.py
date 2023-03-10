from datetime import datetime

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    name: str
    is_disabled: bool
    scopes: list[str]
    registered_at: datetime
