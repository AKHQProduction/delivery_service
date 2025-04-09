from dataclasses import dataclass
from enum import Enum

from delivery_service.domain.shared.dto import Empty


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    full_name: str
    telegram_username: str | Empty


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class Pagination:
    offset: int | Empty = Empty.UNSET
    limit: int | Empty = Empty.UNSET
    order: SortOrder = SortOrder.ASC
