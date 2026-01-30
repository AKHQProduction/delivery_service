from datetime import time
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces.gateways.time_slot_gateway import (
    CreateTimeSlotDTO,
    TimeSlot,
    TimeSlotGateway,
    TimeSlotReadModel,
)
from backend.application.vars import ShopId, TimeSlotId
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot as TimeSlotDB,
)


class SQLAlchemyTimeSlotGateway(TimeSlotGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> TimeSlotId:
        return TimeSlotId(UUID(str(uuid7())))

    async def create(self, dto: CreateTimeSlotDTO) -> None:
        self._session.add(
            TimeSlotDB(
                id=dto.time_slot_id,
                shop_id=dto.shop_id,
                start_time=dto.start_time,
                end_time=dto.end_time,
                label=dto.label,
            )
        )

    async def load(self, time_slot_id: TimeSlotId) -> TimeSlot | None:
        row = await self._session.get(TimeSlotDB, time_slot_id)
        if row:
            return self._to_entity(row)
        return None

    async def load_by_shop(self, shop_id: ShopId) -> list[TimeSlotReadModel]:
        query = (
            select(TimeSlotDB)
            .where(TimeSlotDB.shop_id == shop_id)
            .order_by(TimeSlotDB.start_time)
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

    async def update(self, updated_time_slot: TimeSlot) -> None:
        time_slot_db = await self._session.get(
            TimeSlotDB, updated_time_slot.time_slot_id
        )
        if time_slot_db:
            time_slot_db.start_time = updated_time_slot.start_time
            time_slot_db.end_time = updated_time_slot.end_time
            time_slot_db.label = updated_time_slot.label

    async def delete(self, time_slot_id: TimeSlotId) -> None:
        time_slot_db = await self._session.get(TimeSlotDB, time_slot_id)
        if time_slot_db:
            await self._session.delete(time_slot_db)

    async def exists_by_times_in_shop(
        self, shop_id: ShopId, start_time: time, end_time: time
    ) -> bool:
        query = select(TimeSlotDB).where(
            TimeSlotDB.shop_id == shop_id,
            TimeSlotDB.start_time == start_time,
            TimeSlotDB.end_time == end_time,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_by_shop(self, shop_id: ShopId) -> int:
        query = (
            select(func.count())
            .select_from(TimeSlotDB)
            .where(TimeSlotDB.shop_id == shop_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    @staticmethod
    def _to_entity(row: TimeSlotDB) -> TimeSlot:
        return TimeSlot(
            time_slot_id=TimeSlotId(cast("UUID", cast("object", row.id))),
            shop_id=ShopId(cast("UUID", cast("object", row.shop_id))),
            start_time=cast("time", cast("object", row.start_time)),
            end_time=cast("time", cast("object", row.end_time)),
            label=cast("str | None", cast("object", row.label)),
        )
