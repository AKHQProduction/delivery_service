from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.repository import CustomerRepository


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, customer: Customer) -> None:
        return self._session.add(customer)
