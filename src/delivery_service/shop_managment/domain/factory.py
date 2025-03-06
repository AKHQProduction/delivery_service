from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shop_managment.domain.shop import Shop


@dataclass(frozen=True)
class DaysOffData:
    regular_days: list[int] = field(default_factory=list)
    irregular_days: list[date] = field(default_factory=list)


class ShopFactory(Protocol):
    @abstractmethod
    async def create_shop(
        self,
        shop_name: str,
        shop_location: str,
        shop_days_off: DaysOffData,
        identity_id: UserID,
    ) -> Shop:
        raise NotImplementedError
