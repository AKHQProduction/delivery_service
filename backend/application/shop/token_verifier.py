from abc import abstractmethod
from asyncio import Protocol

from domain.shop.entity.value_objects import ShopToken


class TokenVerifier(Protocol):
    @abstractmethod
    async def verify_token(self, token: ShopToken) -> None:
        raise NotImplementedError
