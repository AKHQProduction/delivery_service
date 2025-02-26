from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from delivery_service.core.shops.shop import Shop
from delivery_service.core.users.user import User


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
        user: User,
    ) -> Shop:
        raise NotImplementedError
