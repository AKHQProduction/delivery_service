from sqlalchemy.ext.asyncio import AsyncSession

from entities.common.entity import BaseEntity
from entities.common.tracker import Tracker


class SATracker(Tracker):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add_one(self, entity: BaseEntity) -> None:
        return self.session.add(entity)

    def add_many(self, entities: list[BaseEntity]) -> None:
        return self.session.add_all(entities)

    async def delete(self, entity: BaseEntity) -> None:
        return await self.session.delete(entity)
