from typing import cast
from uuid import UUID

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.district_gateway import (
    DistrictReadModel,
    GetDistrictsFilters,
)
from backend.application.vars import DistrictId, ShopId
from backend.infrastructure.persistence.tables.districts import District
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyDistrictGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> DistrictId:
        return DistrictId(uuid7())

    def save(self, district: District) -> None:
        self._session.add(district)

    async def load(self, district_id: DistrictId) -> District | None:
        return await self._session.get(District, district_id)

    async def delete(self, district: District) -> None:
        await self._session.delete(district)

    async def read_all(
        self, filters: GetDistrictsFilters, pagination: Pagination
    ) -> list[DistrictReadModel]:
        query = select(District)

        if filters.shop_id:
            query = query.where(District.shop_id == filters.shop_id)
        if filters.name:
            query = query.where(
                District.name.ilike(f"%{escape_like(filters.name)}%")
            )

        if pagination.order == SortOrder.ASC:
            query = query.order_by(asc(District.name), asc(District.id))
        else:
            query = query.order_by(desc(District.name), asc(District.id))

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            DistrictReadModel(
                district_id=DistrictId(cast("UUID", cast("object", row.id))),
                name=cast("str", cast("object", row.name)),
            )
            for row in rows
        ]

    async def exists_by_name_in_shop(self, name: str, shop_id: ShopId) -> bool:
        query = select(
            select(District.id)
            .where(District.name == name, District.shop_id == shop_id)
            .exists()
        )
        result = await self._session.execute(query)
        return result.scalar_one()
