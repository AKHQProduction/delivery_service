from typing import Sequence

from sqlalchemy import RowMapping, Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.address_gateway import (
    AddressGateway,
    AddressGatewayFilters,
    AddressReadModel,
)
from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.infrastructure.persistence.tables.customers import (
    ADDRESSES_TABLE,
)


class SQLAlchemyAddressGateway(AddressGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _set_filters(query: Select, filters: AddressGatewayFilters) -> Select:
        if filters.user_id is not None:
            query = query.where(
                and_(ADDRESSES_TABLE.c.user_id == filters.user_id)
            )

        return query

    @staticmethod
    def _map_row_to_read_model(row: RowMapping) -> AddressReadModel:
        return AddressReadModel(
            address_id=row["id"],
            city=row["city"],
            street=row["street"],
            house_number=row["house_number"],
            apartment_number=row["apartment_number"],
            floor=row["floor"],
            intercom_code=row["intercom_code"],
        )

    @staticmethod
    def _select_rows() -> Select:
        return select(
            ADDRESSES_TABLE.c.id,
            ADDRESSES_TABLE.c.city,
            ADDRESSES_TABLE.c.street,
            ADDRESSES_TABLE.c.house_number,
            ADDRESSES_TABLE.c.apartment_number,
            ADDRESSES_TABLE.c.floor,
            ADDRESSES_TABLE.c.intercom_code,
        )

    async def read_with_id(
        self, address_id: AddressID
    ) -> AddressReadModel | None:
        query = self._select_rows()
        query = query.where(and_(ADDRESSES_TABLE.c.id == address_id))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return None if not row else self._map_row_to_read_model(row)

    async def read_many(
        self, filters: AddressGatewayFilters | None = None
    ) -> Sequence[AddressReadModel]:
        query = self._select_rows()

        if filters:
            query = self._set_filters(query, filters)

        result = await self._session.execute(query)
        return [self._map_row_to_read_model(row) for row in result.mappings()]

    async def total(self, filters: AddressGatewayFilters | None = None) -> int:
        query = select(func.count(ADDRESSES_TABLE.c.id))

        if filters:
            query = self._set_filters(query=query, filters=filters)

        result = await self._session.execute(query)
        return result.scalar_one()
