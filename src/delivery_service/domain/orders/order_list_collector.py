from collections import defaultdict
from collections.abc import Sequence
from datetime import date

from delivery_service.domain.addresses.repository import AddressRepository
from delivery_service.domain.orders.order import DeliveryPreference, Order
from delivery_service.domain.orders.repository import (
    OrderRepository,
    OrderRepositoryFilters,
)
from delivery_service.domain.shops.shop import Shop


class OrderListCollector:
    """
    Service to collect all available orders in proximity order
    from the shop
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        address_repository: AddressRepository,
    ) -> None:
        self._order_repository = order_repository
        self._address_repository = address_repository

    async def collect_orders_by_proximity(
        self, shop: Shop, delivery_date: date
    ) -> dict[DeliveryPreference, Sequence[Order]]:
        all_orders_in_selected_date = await self._order_repository.load_many(
            filters=OrderRepositoryFilters(
                shop_id=shop.id, delivery_date=delivery_date
            )
        )

        orders_with_distance = []
        for order in all_orders_in_selected_date:
            address = await self._address_repository.load_with_id(
                order.address_reference
            )
            if not address:
                continue
            orders_with_distance.append(
                (
                    order,
                    shop.shop_coordinates.distance_to(
                        address.address_coordinates
                    ),
                )
            )
        orders_with_distance.sort(key=lambda x: x[1])

        grouped_orders: dict[DeliveryPreference, list[Order]] = defaultdict(
            list
        )

        for order, _ in orders_with_distance:
            grouped_orders[order.delivery_time_preference].append(order)

        return dict(grouped_orders)
