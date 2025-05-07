from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.infrastructure.persistence.tables.customers import (
    PHONE_NUMBER_TABLE,
)


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, customer: Customer) -> None:
        return self._session.add(customer)

    async def load_with_id(self, customer_id: CustomerID) -> Customer | None:
        return await self._session.get(Customer, customer_id)

    async def delete(self, customer: Customer) -> None:
        return await self._session.delete(customer)

    async def exists_with_number(
        self, shop_id: ShopID, phone_number: str
    ) -> bool:
        query = select(
            exists().where(
                and_(
                    PHONE_NUMBER_TABLE.c.number == phone_number,
                    PHONE_NUMBER_TABLE.c.shop_id == shop_id,
                )
            )
        )

        result = await self._session.execute(query)
        return bool(result.scalar())
