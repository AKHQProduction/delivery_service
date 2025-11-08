from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.vars import ShopId, UserId


@dataclass(frozen=True)
class CreateNewShopDTO:
    shop_id: ShopId
    name: str
    user_id: UserId


class ShopGateway(Protocol):
    @abstractmethod
    async def relate_to_shop(self, user_id: UserId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_shop(self, dto: CreateNewShopDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> ShopId:
        raise NotImplementedError
