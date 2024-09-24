from abc import abstractmethod
from asyncio import Protocol

from entities.order.models import Order, OrderItem


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order: Order) -> None:
        raise NotImplementedError


class OrderItemSaver(Protocol):
    @abstractmethod
    async def save_items(self, order_items: list[OrderItem]) -> None:
        raise NotImplementedError


class OrderReader(Protocol): ...


class OrderItemReader(Protocol): ...
