from abc import abstractmethod
from asyncio import Protocol

from entities.order.models import Order, OrderId, OrderItem


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order: Order) -> None:
        raise NotImplementedError


class OrderItemSaver(Protocol):
    @abstractmethod
    async def save_items(self, order_items: list[OrderItem]) -> None:
        raise NotImplementedError


class OrderReader(Protocol):
    @abstractmethod
    async def by_id(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError


class OrderItemReader(Protocol):
    @abstractmethod
    async def by_order_id(self, order_id: OrderId) -> list[OrderItem]:
        raise NotImplementedError
