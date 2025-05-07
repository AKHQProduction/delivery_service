from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.addresses.address import Address
from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.addresses.repository import AddressRepository
from delivery_service.infrastructure.persistence.tables.customers import (
    ADDRESSES_TABLE,
)


class SQLAlchemyAddressRepository(AddressRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_with_id(self, address_id: AddressID) -> Address | None:
        return await self._session.get(Address, address_id)

    async def load_with_address(
        self, city: str, street: str, house_number: str
    ) -> Address | None:
        query = select(Address).where(
            and_(
                ADDRESSES_TABLE.c.city == city,
                ADDRESSES_TABLE.c.street == street,
                ADDRESSES_TABLE.c.house_number == house_number,
            )
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
