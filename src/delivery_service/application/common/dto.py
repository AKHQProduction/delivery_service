from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None


class Empty(Enum):
    UNSET = "UNSET"


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class Pagination:
    offset: int | Empty = Empty.UNSET
    limit: int | Empty = Empty.UNSET
    order: SortOrder = SortOrder.ASC
