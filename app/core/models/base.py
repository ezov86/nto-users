from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def update_fields(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
