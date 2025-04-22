from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.addresses.address import Address
from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.addresses.repository import AddressRepository


class SQLAlchemyAddressRepository(AddressRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_with_id(self, address_id: AddressID) -> Address | None:
        return await self._session.get(Address, address_id)
