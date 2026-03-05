import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from backend.application.vars import OrderId, RoutePlanId, ShopId, TimeSlotId
from backend.infrastructure.persistence.tables.route_plans import RoutePlan


class SQLAlchemyRoutePlanGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> RoutePlanId:
        return RoutePlanId(uuid7())

    def save(self, route_plan: RoutePlan) -> None:
        self._session.add(route_plan)

    async def load(self, route_plan_id: RoutePlanId) -> RoutePlan | None:
        return await self._session.get(RoutePlan, route_plan_id)

    async def load_by_date(
        self,
        shop_id: ShopId,
        delivery_date: datetime.date,
        time_slot_id: TimeSlotId | None = None,
    ) -> RoutePlan | None:
        query = select(RoutePlan).where(
            RoutePlan.shop_id == shop_id,
            RoutePlan.delivery_date == delivery_date,
        )

        if time_slot_id is not None:
            query = query.where(RoutePlan.time_slot_id == time_slot_id)
        else:
            query = query.where(RoutePlan.time_slot_id.is_(None))

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_order(self, order_id: OrderId) -> RoutePlan | None:
        query = select(RoutePlan).where(
            RoutePlan.order_sequence.contains([order_id]),
        )
        result = await self._session.execute(query)
        return result.scalars().first()
