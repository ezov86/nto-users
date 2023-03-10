from typing import TypeVar, Generic, Type

from sqlalchemy.orm import Session

from app.core import models


class ModelNotFoundError(Exception):
    def __init__(self, msg="Model not found"):
        super().__init__(msg)


ModelType = TypeVar("ModelType", bound=models.Base)


class BaseRepo(Generic[ModelType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, id_: int) -> ModelType | None:
        # noinspection PyTypeChecker
        return self.session.query(self.model).where(
            self.model.id == id_
        ).first()

    def get_many(self, offset: int, limit: int) -> list[ModelType]:
        # noinspection PyTypeChecker
        return self.session.query(self.model).offset(offset).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: ModelType):
        self.session.delete(obj)
        self.session.commit()
