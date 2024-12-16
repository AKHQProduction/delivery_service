from abc import abstractmethod
from asyncio import Protocol

from entities.common.entity import BaseEntity


class Tracker(Protocol):
    @abstractmethod
    def add_one(self, entity: BaseEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_many(self, entities: list[BaseEntity]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: BaseEntity) -> None:
        raise NotImplementedError
