from dataclasses import dataclass
from typing import TypeVar, Union

OIDType = TypeVar("OIDType")


@dataclass
class BaseEntity:
    oid: OIDType

    def __hash__(self) -> int:
        return hash(self.oid)

    def __eq__(self, other: Union[object, "BaseEntity"]) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.oid == other.oid
