from dataclasses import dataclass
from enum import StrEnum


class SortOrder(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class Pagination:
    offset: int = 0
    limit: int = 100
    order: SortOrder = SortOrder.ASC
