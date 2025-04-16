from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.repository import CustomerRepository
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables import CUSTOMERS_TABLE


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, customer: Customer) -> None:
        return self._session.add(customer)

    async def exists(self, phone_number: str, shop_id: ShopID) -> bool:
        query = select(
            exists().where(
                and_(
                    or_(
                        func.jsonb_extract_path_text(
                            CUSTOMERS_TABLE.c.contacts, "primary", "value"
                        )
                        == phone_number,
                        func.jsonb_extract_path_text(
                            CUSTOMERS_TABLE.c.contacts, "secondary", "value"
                        )
                        == phone_number,
                    ),
                    CUSTOMERS_TABLE.c.shop_id == shop_id,
                )
            )
        )

        result = await self._session.execute(query)
        return bool(result.scalar())

    async def load_with_id(self, customer_id: UserID) -> Customer | None:
        return await self._session.get(Customer, customer_id)

    async def delete(self, customer: Customer) -> None:
        return await self._session.delete(customer)
