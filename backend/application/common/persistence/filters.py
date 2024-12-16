from dataclasses import dataclass
from enum import Enum


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class Pagination:
    offset: int | None = None
    limit: int | None = None
    order: SortOrder = SortOrder.ASC
