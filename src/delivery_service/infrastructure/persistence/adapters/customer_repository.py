from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.infrastructure.persistence.tables import CUSTOMERS_TABLE


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, customer: Customer) -> None:
        return self._session.add(customer)

    async def exists(self, phone_number: str) -> bool:
        query = select(
            exists().where(
                or_(
                    func.jsonb_extract_path_text(
                        CUSTOMERS_TABLE.c.contacts, "primary", "value"
                    )
                    == phone_number,
                    func.jsonb_extract_path_text(
                        CUSTOMERS_TABLE.c.contacts, "secondary", "value"
                    )
                    == phone_number,
                )
            )
        )

        result = await self._session.execute(query)
        return bool(result.scalar())
