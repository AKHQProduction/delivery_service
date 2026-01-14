import uuid
from collections import defaultdict

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    GetOrdersFilters,
    Order,
    OrderGateway,
    OrderItemDTO,
    OrderItemReadModel,
    OrderReadModel,
    OrderStatsReadModel,
    PaymentMethodStatsReadModel,
    UpdateOrderDTO,
)
from backend.application.vars import (
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PaymentMethod,
    ShopId,
    TimePreference,
)


class InMemoryOrderGateway(OrderGateway):
    def __init__(self, order_id: OrderId | None = None) -> None:
        self.orders: dict[OrderId, CreateOrderDTO] = {}
        self.order_id = order_id
        self.client_names: dict[ClientId, str] = {}
        self.client_custom_ids: dict[ClientId, str | None] = {}

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

        if filters.client_name or filters.custom_id:

            def matches_search(order: CreateOrderDTO) -> bool:
                client_name = self.client_names.get(order.client_id, "")
                custom_id = self.client_custom_ids.get(order.client_id, "")
                name_match = (
                    filters.client_name
                    and filters.client_name.lower() in client_name.lower()
                )
                custom_id_match = (
                    filters.custom_id
                    and custom_id
                    and filters.custom_id.lower() in custom_id.lower()
                )
                return bool(name_match or custom_id_match)

            filtered_orders = [o for o in filtered_orders if matches_search(o)]

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
                    name=item.name or "",
                    quantity=item.quantity,
                    price_per_item=item.price_per_item or 0,
                    product_id=item.product_id,
                )
                for idx, item in enumerate(dto.order_items)
            ],
        )

    async def update(self, dto: UpdateOrderDTO) -> None:
        existing = self.orders.get(dto.order_id)
        if not existing:
            return

        comment = self._resolve_comment(dto.comment, existing.comment)
        items = self._process_update_items(dto.items, existing.order_items)

        updated_order = CreateOrderDTO(
            order_id=existing.order_id,
            shop_id=existing.shop_id,
            client_id=dto.client_id or existing.client_id,
            delivery_date=dto.delivery_date or existing.delivery_date,
            time_preference=dto.time_preference or existing.time_preference,
            delivery_phone=dto.delivery_phone or existing.delivery_phone,
            delivery_address=dto.delivery_address or existing.delivery_address,
            order_items=items,
            payment_method=dto.payment_method or existing.payment_method,
            comment=comment,
        )

        self.orders[dto.order_id] = updated_order

    def _resolve_comment(
        self, new_comment: str | Empty | None, existing_comment: str | None
    ) -> str | None:
        if new_comment is None:
            return existing_comment
        return None if new_comment == Empty.EMPTY else new_comment

    def _process_update_items(
        self,
        new_items: list[OrderItemDTO] | None,
        existing_items: list[OrderItemDTO],
    ) -> list[OrderItemDTO]:
        if new_items is None:
            return list(existing_items)

        existing_map = {i.id: i for i in existing_items if i.id is not None}
        max_id = max((i.id or 0 for i in existing_items), default=0)
        result: list[OrderItemDTO] = []

        for item in new_items:
            if item.id is not None:
                existing = existing_map.get(item.id)
                result.append(
                    OrderItemDTO(
                        quantity=item.quantity,
                        name=item.name or (existing.name if existing else ""),
                        price_per_item=item.price_per_item
                        or (existing.price_per_item if existing else 0),
                        id=item.id,
                        product_id=item.product_id
                        or (existing.product_id if existing else None),
                    )
                )
            else:
                max_id += 1
                result.append(
                    OrderItemDTO(
                        quantity=item.quantity,
                        name=item.name or "",
                        price_per_item=item.price_per_item or 0,
                        id=OrderItemId(max_id),
                        product_id=item.product_id,
                    )
                )

        return result

    async def load_items(self, order_id: OrderId) -> list[OrderItemReadModel]:
        dto = self.orders.get(order_id)
        if not dto:
            return []
        return [
            OrderItemReadModel(
                id=item.id or idx + 1,
                name=item.name or "",
                quantity=item.quantity,
                price_per_item=item.price_per_item or 0,
                product_id=item.product_id,
            )
            for idx, item in enumerate(dto.order_items)
        ]

    async def get_stats(
        self, filters: GetOrdersFilters
    ) -> OrderStatsReadModel:
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

        total_orders = len(filtered_orders)
        total_orders_in_first_half = sum(
            1
            for o in filtered_orders
            if o.time_preference == TimePreference.FIRST_HALF
        )
        total_orders_in_second_half = sum(
            1
            for o in filtered_orders
            if o.time_preference == TimePreference.SECOND_HALF
        )
        total_orders_sum = sum(
            (item.quantity * (item.price_per_item or 0))
            for o in filtered_orders
            for item in o.order_items
        )

        payment_method_sums: dict[str, int] = defaultdict(int)
        for o in filtered_orders:
            order_sum = sum(
                item.quantity * (item.price_per_item or 0)
                for item in o.order_items
            )
            payment_method_sums[o.payment_method.value] += order_sum

        payment_method_stats = [
            PaymentMethodStatsReadModel(
                method=PaymentMethod(method),
                orders_sum=orders_sum,
            )
            for method, orders_sum in payment_method_sums.items()
        ]

        return OrderStatsReadModel(
            total_orders=total_orders,
            total_orders_in_first_half=total_orders_in_first_half,
            total_orders_in_second_half=total_orders_in_second_half,
            total_orders_sum=total_orders_sum,
            category_stats=[],
            payment_method_stats=payment_method_stats,
        )
