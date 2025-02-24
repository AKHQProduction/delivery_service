from typing import Generic, Hashable, TypeVar

# Object ID
EntityID = TypeVar("EntityID", bound=Hashable)


class Entity(Generic[EntityID]):
    def __init__(self, entity_id: EntityID) -> None:
        self._entity_id = entity_id

    @property
    def entity_id(self) -> EntityID:
        return self._entity_id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Entity):
            return bool(other._entity_id == self._entity_id)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._entity_id)
