from typing import Generic, Hashable, TypeVar

# Object ID
OID = TypeVar("OID", bound=Hashable)


class Entity(Generic[OID]):
    def __init__(self, oid: OID) -> None:
        self.oid = oid

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Entity):
            return bool(other.oid == self.oid)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.oid)
