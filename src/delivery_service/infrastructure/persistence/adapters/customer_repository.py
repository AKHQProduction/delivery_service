from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shared.user_id import UserID


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, customer: Customer) -> None:
        return self._session.add(customer)

    async def load_with_id(self, customer_id: UserID) -> Customer | None:
        return await self._session.get(Customer, customer_id)

    async def delete(self, customer: Customer) -> None:
        return await self._session.delete(customer)
