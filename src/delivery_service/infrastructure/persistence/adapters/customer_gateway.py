from typing import Sequence

from sqlalchemy import JSON, RowMapping, Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.address_gateway import (
    AddressReadModel,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
    CustomerGatewayFilters,
    CustomerReadModel,
)
from delivery_service.domain.customers.phone_number import PhoneBook
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables import (
    CUSTOMERS_TABLE,
    USERS_TABLE,
)
from delivery_service.infrastructure.persistence.tables.customers import (
    ADDRESSES_TABLE,
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
        contacts: PhoneBook = row["contacts"]
        addresses_raw: list[dict] = row["delivery_addresses"] or []

        return CustomerReadModel(
            customer_id=row["customer_id"],
            full_name=row["full_name"],
            primary_phone=contacts.primary_phone,
            delivery_addresses=[
                AddressReadModel(
                    address_id=addr["id"],
                    city=addr["city"],
                    street=addr["street"],
                    house_number=addr["house_number"],
                    apartment_number=addr.get("apartment_number"),
                    floor=addr.get("floor"),
                    intercom_code=addr.get("intercom_code"),
                )
                for addr in addresses_raw
            ],
        )

    @staticmethod
    def _select_rows() -> Select:
        addr_obj = func.json_build_object(
            "id",
            ADDRESSES_TABLE.c.id,
            "city",
            ADDRESSES_TABLE.c.city,
            "street",
            ADDRESSES_TABLE.c.street,
            "house_number",
            ADDRESSES_TABLE.c.house_number,
            "apartment_number",
            ADDRESSES_TABLE.c.apartment_number,
            "floor",
            ADDRESSES_TABLE.c.floor,
            "intercom_code",
            ADDRESSES_TABLE.c.intercom_code,
        )
        from sqlalchemy import cast

        addr_agg = func.coalesce(
            func.json_agg(addr_obj).filter(
                ADDRESSES_TABLE.c.user_id.isnot(None)
            ),
            cast("[]", JSON),
        ).label("delivery_addresses")

        return (
            select(
                CUSTOMERS_TABLE.c.user_id.label("customer_id"),
                USERS_TABLE.c.full_name,
                CUSTOMERS_TABLE.c.contacts,
                addr_agg,
            )
            .join(
                USERS_TABLE,
                and_(USERS_TABLE.c.id == CUSTOMERS_TABLE.c.user_id),
            )
            .outerjoin(
                ADDRESSES_TABLE,
                and_(ADDRESSES_TABLE.c.user_id == CUSTOMERS_TABLE.c.user_id),
            )
            .group_by(
                CUSTOMERS_TABLE.c.user_id,
                USERS_TABLE.c.full_name,
                CUSTOMERS_TABLE.c.contacts,
            )
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
