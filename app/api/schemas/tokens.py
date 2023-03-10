from pydantic import BaseModel


class AuthTokensSchema(BaseModel):
    access: str
    refresh: str
