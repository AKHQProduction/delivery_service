from datetime import date

from geoalchemy2 import Geography
from sqlalchemy import Float, and_, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.order_list_collector import (
    OrderListCollector,
)
from delivery_service.domain.orders.order import DeliveryPreference, Order
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.address import Coordinates
from delivery_service.infrastructure.persistence.tables import ORDERS_TABLE
from delivery_service.infrastructure.persistence.tables.customers import (
    ADDRESSES_TABLE,
)

SRID = 4326


class SQLAlchemyOrdrLictCollector(OrderListCollector):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def collect_orders_by_proximity(
        self,
        shop_id: ShopID,
        shop_coordinates: Coordinates,
        delivery_date: date,
    ) -> dict[DeliveryPreference, list[Order]]:
        address = ADDRESSES_TABLE.c
        order = ORDERS_TABLE.c

        start_point = func.ST_SetSRID(
            func.ST_MakePoint(
                shop_coordinates.latitude, shop_coordinates.longitude
            ),
            SRID,
        ).cast(Geography)

        address_latitude = cast(address.coordinates["latitude"], Float)
        address_longitude = cast(address.coordinates["longitude"], Float)

        address_point = func.ST_SetSRID(
            func.ST_MakePoint(address_longitude, address_latitude), SRID
        ).cast(Geography)

        # IN METERS !!!
        distance_query = func.ST_Distance(start_point, address_point).label(
            "distance"
        )

        query = (
            select(Order)
            .join(ADDRESSES_TABLE, and_(order.address_id == address.id))
            .where(
                and_(
                    order.shop_id == shop_id,
                    order.delivery_date == delivery_date,
                )
            )
            .order_by(distance_query)
        )

        result = await self._session.execute(query)
        orders_sorted: list[Order] = list(result.scalars().all())

        grouped: dict[DeliveryPreference, list[Order]] = {
            DeliveryPreference.MORNING: [],
            DeliveryPreference.AFTERNOON: [],
        }
        for order in orders_sorted:
            grouped[order.delivery_time_preference].append(order)

        return grouped
