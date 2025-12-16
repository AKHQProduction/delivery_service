import uuid

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    GetOrdersFilters,
    Order,
    OrderGateway,
    OrderItemDTO,
    OrderItemReadModel,
    OrderReadModel,
    UpdateOrderDTO,
)
from backend.application.vars import (
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    ShopId,
)


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
                    id=item.id or idx + 1,
                    name=item.name,
                    quantity=item.quantity,
                    price_per_item=item.price_per_item,
                )
                for idx, item in enumerate(dto.order_items)
            ],
        )

    async def update(self, dto: UpdateOrderDTO) -> None:
        existing = self.orders.get(dto.order_id)
        if not existing:
            return

        new_client_id = (
            dto.client_id if dto.client_id is not None else existing.client_id
        )
        new_delivery_date = (
            dto.delivery_date
            if dto.delivery_date is not None
            else existing.delivery_date
        )
        new_time_preference = (
            dto.time_preference
            if dto.time_preference is not None
            else existing.time_preference
        )
        new_delivery_phone = (
            dto.delivery_phone
            if dto.delivery_phone is not None
            else existing.delivery_phone
        )
        new_delivery_address = (
            dto.delivery_address
            if dto.delivery_address is not None
            else existing.delivery_address
        )

        if dto.comment is not None:
            new_comment = None if dto.comment == Empty.EMPTY else dto.comment
        else:
            new_comment = existing.comment

        # Process items
        current_items = list(existing.order_items)

        # Delete items
        if dto.items_to_delete:
            current_items = [
                item
                for item in current_items
                if item.id not in dto.items_to_delete
            ]

        # Update existing items
        if dto.items_to_update:
            updated_items = []
            for item in current_items:
                update_item = next(
                    (u for u in dto.items_to_update if u.id == item.id), None
                )
                if update_item:
                    updated_items.append(
                        OrderItemDTO(
                            id=item.id,
                            name=update_item.name or item.name,
                            quantity=(update_item.quantity or item.quantity),
                            price_per_item=(
                                update_item.price_per_item
                                or item.price_per_item
                            ),
                        )
                    )
                else:
                    updated_items.append(item)
            current_items = updated_items

        # Add new items
        if dto.items_to_add:
            max_id = max((item.id or 0 for item in current_items), default=0)
            for add_item in dto.items_to_add:
                max_id += 1
                current_items.append(
                    OrderItemDTO(
                        id=OrderItemId(max_id),
                        name=add_item.name,
                        quantity=add_item.quantity,
                        price_per_item=add_item.price_per_item,
                    )
                )

        updated_order = CreateOrderDTO(
            order_id=existing.order_id,
            shop_id=existing.shop_id,
            client_id=new_client_id,
            delivery_date=new_delivery_date,
            time_preference=new_time_preference,
            delivery_phone=new_delivery_phone,
            delivery_address=new_delivery_address,
            order_items=current_items,
            comment=new_comment,
        )

        self.orders[dto.order_id] = updated_order
