from datetime import time
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from backend.application.interfaces.gateways.time_slot_gateway import (
    TimeSlotReadModel,
)
from backend.application.vars import ShopId, TimeSlotId
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)


class SQLAlchemyTimeSlotGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> TimeSlotId:
        return TimeSlotId(uuid7())

    def save(self, time_slot: ShopDeliveryTimeSlot) -> None:
        self._session.add(time_slot)

    async def load(
        self, time_slot_id: TimeSlotId
    ) -> ShopDeliveryTimeSlot | None:
        return await self._session.get(ShopDeliveryTimeSlot, time_slot_id)

    async def load_by_shop(self, shop_id: ShopId) -> list[TimeSlotReadModel]:
        query = (
            select(ShopDeliveryTimeSlot)
            .where(ShopDeliveryTimeSlot.shop_id == shop_id)
            .order_by(ShopDeliveryTimeSlot.start_time)
        )

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            TimeSlotReadModel(
                time_slot_id=TimeSlotId(cast("UUID", cast("object", row.id))),
                start_time=cast(
                    "time", cast("object", row.start_time)
                ).strftime("%H:%M"),
                end_time=cast("time", cast("object", row.end_time)).strftime(
                    "%H:%M"
                ),
                label=cast("str | None", cast("object", row.label)),
            )
            for row in rows
        ]

    async def delete(self, time_slot: ShopDeliveryTimeSlot) -> None:
        await self._session.delete(time_slot)

    async def exists_by_times_in_shop(
        self, shop_id: ShopId, start_time: time, end_time: time
    ) -> bool:
        query = select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.shop_id == shop_id,
            ShopDeliveryTimeSlot.start_time == start_time,
            ShopDeliveryTimeSlot.end_time == end_time,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_by_shop(self, shop_id: ShopId) -> int:
        query = (
            select(func.count())
            .select_from(ShopDeliveryTimeSlot)
            .where(ShopDeliveryTimeSlot.shop_id == shop_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one()
