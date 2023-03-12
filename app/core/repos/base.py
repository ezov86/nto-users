from app.core import exc
from typing import TypeVar, Generic, Type

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import models

ModelType = TypeVar("ModelType", bound=models.Base)


class BaseRepo(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id_: int) -> ModelType | None:
        return await self.session.get(self.model, id_)

    async def get_many(self, offset: int, limit: int) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        # noinspection PyTypeChecker
        return result.all()

    async def create(self, obj: ModelType, attribute_names: list[str] = None) -> ModelType:
        """
        :raises AlreadyExists: given model is not unique (if it should be).
        """

        if attribute_names is None:
            attribute_names = []

        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj, attribute_names)
        except IntegrityError:
            raise exc.AlreadyExists(self.model.__name__)

        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """
        :raises AlreadyExists: model with updated unique data already exists.
        """
        try:
            await self.session.commit()
            await self.session.refresh(obj)
        except IntegrityError:
            raise exc.AlreadyExists(self.model.__name__)

        return obj

    async def delete(self, obj: ModelType):
        await self.session.delete(obj)
        await self.session.commit()
