import uuid

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    GetOrdersFilters,
    Order,
    OrderGateway,
    OrderItemReadModel,
    OrderReadModel,
)
from backend.application.vars import ClientId, OrderId, ShopId


class InMemoryOrderGateway(OrderGateway):
    def __init__(self, order_id: OrderId | None = None) -> None:
        self.orders: dict[OrderId, CreateOrderDTO] = {}
        self.order_id = order_id
        self.client_names: dict[ClientId, str] = {}

    def next_id(self) -> OrderId:
        return self.order_id or OrderId(uuid.uuid4())

    async def create_order(self, dto: CreateOrderDTO) -> None:
        self.orders[dto.order_id] = dto

    async def load(self, order_id: OrderId) -> Order | None:
        dto = self.orders.get(order_id)
        if dto:
            return Order(
                order_id=dto.order_id,
                shop_id=dto.shop_id,
                client_id=dto.client_id,
                delivery_date=dto.delivery_date,
                time_preference=dto.time_preference,
                delivery_phone=dto.delivery_phone,
                delivery_address=dto.delivery_address,
                comment=dto.comment,
            )
        return None

    async def delete(self, order_id: OrderId) -> None:
        if order_id in self.orders:
            del self.orders[order_id]

    async def read(
        self, order_id: OrderId, shop_id: ShopId
    ) -> OrderReadModel | None:
        dto = self.orders.get(order_id)
        if dto and dto.shop_id == shop_id:
            return self._to_read_model(dto)
        return None

    async def read_all(
        self, filters: GetOrdersFilters, pagination: Pagination
    ) -> list[OrderReadModel]:
        filtered_orders = list(self.orders.values())

        if filters.shop_id:
            filtered_orders = [
                o for o in filtered_orders if o.shop_id == filters.shop_id
            ]
        if filters.delivery_date:
            filtered_orders = [
                o
                for o in filtered_orders
                if o.delivery_date == filters.delivery_date
            ]
        if filters.time_preference:
            filtered_orders = [
                o
                for o in filtered_orders
                if o.time_preference == filters.time_preference
            ]

        filtered_orders.sort(key=lambda o: o.delivery_date)

        start = pagination.offset
        end = start + pagination.limit
        paginated_orders = filtered_orders[start:end]

        return [self._to_read_model(dto) for dto in paginated_orders]

    def _to_read_model(self, dto: CreateOrderDTO) -> OrderReadModel:
        return OrderReadModel(
            order_id=dto.order_id,
            date=dto.delivery_date,
            time_preference=dto.time_preference,
            delivery_phone=dto.delivery_phone,
            delivery_address=dto.delivery_address,
            comment=dto.comment,
            client_id=dto.client_id,
            client_name=self.client_names.get(dto.client_id, "Unknown"),
            items=[
                OrderItemReadModel(
                    id=idx + 1,
                    name=item.name,
                    quantity=item.quantity,
                    price_per_item=item.price_per_item,
                )
                for idx, item in enumerate(dto.order_items)
            ],
        )
