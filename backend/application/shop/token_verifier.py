from abc import abstractmethod
from asyncio import Protocol

from entities.shop.models.value_objects import ShopToken


class TokenVerifier(Protocol):
    @abstractmethod
    async def verify_token(self, token: ShopToken) -> None:
        raise NotImplementedError
