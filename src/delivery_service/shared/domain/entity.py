from typing import TYPE_CHECKING, Generic, Hashable, TypeVar

if TYPE_CHECKING:
    from delivery_service.shared.domain.tracker import Tracker

# Object ID
EntityID = TypeVar("EntityID", bound=Hashable)


class Entity(Generic[EntityID]):
    def __init__(self, entity_id: EntityID, tracker: "Tracker") -> None:
        self._entity_id = entity_id
        self._tracker = tracker

    def add_one(self) -> None:
        self._tracker.add_new(self)

    async def delete_one(self) -> None:
        await self._tracker.delete(self)

    @property
    def entity_id(self) -> EntityID:
        return self._entity_id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Entity):
            return bool(other._entity_id == self._entity_id)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._entity_id)
