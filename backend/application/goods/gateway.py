from abc import abstractmethod
from asyncio import Protocol

from entities.goods.models import Goods


class GoodsSaver(Protocol):
    @abstractmethod
    async def save(self, goods: Goods) -> None:
        raise NotImplementedError
