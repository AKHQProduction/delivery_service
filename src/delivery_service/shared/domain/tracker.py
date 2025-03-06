from abc import abstractmethod
from asyncio import Protocol

from delivery_service.shared.domain.entity import Entity


class Tracker(Protocol):
    @abstractmethod
    def add_new(self, entity: Entity) -> None: ...

    @abstractmethod
    async def delete(self, entity: Entity) -> None: ...
