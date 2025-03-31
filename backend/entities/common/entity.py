from dataclasses import dataclass
from typing import Generic, TypeVar, Union

OIDType = TypeVar("OIDType")


@dataclass
class BaseEntity(Generic[OIDType]):
    oid: OIDType | None

    def __hash__(self) -> int:
        return hash(self.oid)

    def __eq__(self, other: Union[object, "BaseEntity"]) -> bool:
        if not isinstance(other, type(self)) or self.oid is None:
            return NotImplemented
        return self.oid == other.oid
