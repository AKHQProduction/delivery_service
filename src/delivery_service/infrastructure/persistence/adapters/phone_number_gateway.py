from sqlalchemy import RowMapping, Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.phone_number_gateway import (
    PhoneNumberGateway,
    PhoneNumberReadModel,
)
from delivery_service.domain.customers.phone_number_id import PhoneNumberID
from delivery_service.infrastructure.persistence.tables.customers import (
    PHONE_NUMBER_TABLE,
)


class SQLAlchemyPhoneNumberGateway(PhoneNumberGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _map_row_to_read_model(row: RowMapping) -> PhoneNumberReadModel:
        return PhoneNumberReadModel(
            phone_number_id=row["id"],
            number=row["number"],
            is_primary=row["is_primary"],
        )

    @staticmethod
    def _select_rows() -> Select:
        return select(
            PHONE_NUMBER_TABLE.c.id,
            PHONE_NUMBER_TABLE.c.number,
            PHONE_NUMBER_TABLE.c.is_primary,
        )

    async def read_with_id(
        self, phone_number_id: PhoneNumberID
    ) -> PhoneNumberReadModel | None:
        query = self._select_rows()
        query = query.where(and_(PHONE_NUMBER_TABLE.c.id == phone_number_id))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return None if not row else self._map_row_to_read_model(row)
