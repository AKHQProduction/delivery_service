# ruff: noqa: E501

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.customer_registries.customer_registry import (
    CustomerRegistry,
)
from delivery_service.domain.customer_registries.customer_registry_repository import (
    CustomerRegistryRepository,
)
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables.shops import (
    STAFF_MEMBERS_TABLE,
)


class SQLAlchemyCustomerRegistryRepository(CustomerRegistryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_with_identity(
        self, identity_id: UserID
    ) -> CustomerRegistry | None:
        query = select(CustomerRegistry).join(
            STAFF_MEMBERS_TABLE,
            and_(STAFF_MEMBERS_TABLE.c.user_id == identity_id),
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
