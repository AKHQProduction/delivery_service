from abc import abstractmethod
from asyncio import Protocol

from application.common.persistence.view_models import OrderView
from entities.order.models import Order, OrderId, OrderItemId


class OrderGateway(Protocol):
    @abstractmethod
    async def load_with_id(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_item_id(
        self, order_item_id: OrderItemId
    ) -> Order | None:
        raise NotImplementedError


class OrderReader(Protocol):
    @abstractmethod
    async def read_with_id(self, order_id: OrderId) -> OrderView | None:
        raise NotImplementedError
