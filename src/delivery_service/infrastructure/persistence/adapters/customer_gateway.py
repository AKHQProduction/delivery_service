import json
from typing import Sequence

from sqlalchemy import (
    JSON,
    RowMapping,
    Select,
    and_,
    cast,
    func,
    label,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.address_gateway import (
    AddressReadModel,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
    CustomerGatewayFilters,
    CustomerReadModel,
)
from delivery_service.application.query.ports.phone_number_gateway import (
    PhoneNumberReadModel,
)
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.infrastructure.persistence.tables import (
    CUSTOMERS_TABLE,
)
from delivery_service.infrastructure.persistence.tables.customers import (
    ADDRESSES_TABLE,
    PHONE_NUMBER_TABLE,
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
        raw_addresses = row["addresses"]
        if isinstance(raw_addresses, str):
            try:
                addr_list = json.loads(raw_addresses)
            except json.JSONDecodeError:
                addr_list = []
        else:
            addr_list = raw_addresses or []
        addresses = [
            AddressReadModel(
                address_id=addr.get("address_id"),
                city=addr.get("city"),
                street=addr.get("street"),
                house_number=addr.get("house_number"),
                apartment_number=addr.get("apartment_number"),
                floor=addr.get("floor"),
                intercom_code=addr.get("intercom_code"),
            )
            for addr in addr_list
        ]

        raw_phones = row["phone_numbers"]
        if isinstance(raw_phones, str):
            try:
                phone_list = json.loads(raw_phones)
            except json.JSONDecodeError:
                phone_list = []
        else:
            phone_list = raw_phones or []
        phone_numbers = [
            PhoneNumberReadModel(
                phone_number_id=ph.get("phone_number_id"),
                number=ph.get("number"),
                is_primary=ph.get("is_primary"),
            )
            for ph in phone_list
        ]

        return CustomerReadModel(
            customer_id=row["id"],
            name=row["name"],
            addresses=addresses,
            phone_numbers=phone_numbers,
        )

    @staticmethod
    def _select_rows() -> Select:
        return (
            select(
                CUSTOMERS_TABLE.c.id,
                CUSTOMERS_TABLE.c.name,
                label(
                    "addresses",
                    func.coalesce(
                        func.json_agg(
                            func.json_build_object(
                                "address_id",
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
                        ).filter(ADDRESSES_TABLE.c.id.is_not(None)),
                        cast("[]", JSON),
                    ),
                ),
                label(
                    "phone_numbers",
                    func.coalesce(
                        func.json_agg(
                            func.json_build_object(
                                "phone_number_id",
                                PHONE_NUMBER_TABLE.c.id,
                                "number",
                                PHONE_NUMBER_TABLE.c.number,
                                "is_primary",
                                PHONE_NUMBER_TABLE.c.is_primary,
                            )
                        ).filter(PHONE_NUMBER_TABLE.c.id.is_not(None)),
                        cast("[]", JSON),
                    ),
                ),
            )
            .select_from(CUSTOMERS_TABLE)
            .outerjoin(
                ADDRESSES_TABLE,
                and_(ADDRESSES_TABLE.c.customer_id == CUSTOMERS_TABLE.c.id),
            )
            .outerjoin(
                PHONE_NUMBER_TABLE,
                and_(PHONE_NUMBER_TABLE.c.customer_id == CUSTOMERS_TABLE.c.id),
            )
            .group_by(CUSTOMERS_TABLE.c.id, CUSTOMERS_TABLE.c.name)
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
        self, customer_id: CustomerID
    ) -> CustomerReadModel | None:
        query = self._select_rows()
        query = query.where(and_(CUSTOMERS_TABLE.c.id == customer_id))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return self._map_row_to_read_model(row) if row else None

    async def read_with_phone(self, phone: str) -> CustomerReadModel | None:
        query = self._select_rows()
        query = query.where(and_(PHONE_NUMBER_TABLE.c.number == phone))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return self._map_row_to_read_model(row) if row else None

    async def total(
        self, filters: CustomerGatewayFilters | None = None
    ) -> int:
        query = select(func.count(CUSTOMERS_TABLE.c.id))

        if filters:
            query = self._set_filters(query=query, filters=filters)

        result = await self._session.execute(query)
        return result.scalar_one()
