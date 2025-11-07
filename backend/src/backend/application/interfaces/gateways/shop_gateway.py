from abc import abstractmethod
from typing import Protocol

from backend.application.vars import UserId


class ShopGateway(Protocol):
    @abstractmethod
    async def relate_to_shop(self, user_id: UserId) -> bool:
        raise NotImplementedError
