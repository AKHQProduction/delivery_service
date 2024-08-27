from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class UserDTO:
    user_id: int
    full_name: str
    username: str | None
    phone_number: str | None


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class Pagination:
    offset: int | None = None
    limit: int | None = None
    order: SortOrder = SortOrder.ASC
