from typing import Sequence

from sqlalchemy import RowMapping, Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
    CustomerGatewayFilters,
    CustomerReadModel,
)
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables import (
    CUSTOMERS_TABLE,
)


class SQLAlchemyCustomerGateway(CustomerGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _set_filters(query: Select, filters: CustomerGatewayFilters) -> Select:
        if filters.shop_id is not None:
            query = query.where(
                and_(CUSTOMERS_TABLE.c.shop_id == filters.shop_id)
            )

        return query

    @staticmethod
    def _map_row_to_read_model(row: RowMapping) -> CustomerReadModel:
        return CustomerReadModel(
            customer_id=row["id"],
            name=row["name"],
        )

    @staticmethod
    def _select_rows() -> Select:
        return select(
            CUSTOMERS_TABLE.c.id,
            CUSTOMERS_TABLE.c.name,
        )

    async def read_all_customers(
        self, filters: CustomerGatewayFilters | None = None
    ) -> Sequence[CustomerReadModel]:
        query = self._select_rows()

        if filters:
            query = self._set_filters(query, filters)

        result = await self._session.execute(query)
        return [self._map_row_to_read_model(row) for row in result.mappings()]

    async def read_with_id(
        self, customer_id: UserID
    ) -> CustomerReadModel | None:
        query = self._select_rows()
        query = query.where(and_(CUSTOMERS_TABLE.c.user_id == customer_id))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return self._map_row_to_read_model(row) if row else None

    async def read_with_phone(self, phone: str) -> CustomerReadModel | None:
        query = self._select_rows()
        query = query.where(
            or_(
                func.jsonb_extract_path_text(
                    CUSTOMERS_TABLE.c.contacts, "primary", "value"
                )
                == phone,
                func.jsonb_extract_path_text(
                    CUSTOMERS_TABLE.c.contacts, "secondary", "value"
                )
                == phone,
            )
        )

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return self._map_row_to_read_model(row) if row else None

    async def total(
        self, filters: CustomerGatewayFilters | None = None
    ) -> int:
        query = select(func.count(CUSTOMERS_TABLE.c.user_id))

        if filters:
            query = self._set_filters(query=query, filters=filters)

        result = await self._session.execute(query)
        return result.scalar_one()
