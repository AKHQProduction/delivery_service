from dataclasses import dataclass
from enum import Enum


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class Pagination:
    offset: int = 0
    limit: int = 100
    order: SortOrder = SortOrder.ASC
