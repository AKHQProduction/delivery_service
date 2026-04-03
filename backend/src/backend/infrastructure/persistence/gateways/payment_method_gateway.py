from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils.compat import uuid7

from backend.application.dto.gateways.payment_method_gateway import (
    PaymentMethodReadModel,
)
from backend.application.vars import PaymentMethodId, ShopId
from backend.infrastructure.persistence.tables.shops import (
    ShopPaymentMethod,
)
from backend.infrastructure.persistence.utils.cast import mapped_cast


class SQLAlchemyPaymentMethodGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> PaymentMethodId:
        return PaymentMethodId(uuid7())

    def save(self, payment_method: ShopPaymentMethod) -> None:
        self._session.add(payment_method)

    async def load(
        self, payment_method_id: PaymentMethodId
    ) -> ShopPaymentMethod | None:
        return await self._session.get(ShopPaymentMethod, payment_method_id)

    async def load_by_shop(
        self, shop_id: ShopId
    ) -> list[PaymentMethodReadModel]:
        query = (
            select(ShopPaymentMethod)
            .where(ShopPaymentMethod.shop_id == shop_id)
            .order_by(ShopPaymentMethod.created_at)
        )

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            PaymentMethodReadModel(
                payment_method_id=PaymentMethodId(mapped_cast(UUID, row.id)),
                name=mapped_cast(str, row.name),
            )
            for row in rows
        ]

    async def delete(self, payment_method: ShopPaymentMethod) -> None:
        await self._session.delete(payment_method)

    async def exists_by_name_in_shop(self, shop_id: ShopId, name: str) -> bool:
        query = select(ShopPaymentMethod).where(
            ShopPaymentMethod.shop_id == shop_id,
            ShopPaymentMethod.name == name,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_by_shop(self, shop_id: ShopId) -> int:
        query = (
            select(func.count())
            .select_from(ShopPaymentMethod)
            .where(ShopPaymentMethod.shop_id == shop_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one()
