from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.input_data import Pagination, SortOrder
from application.shop.errors import ShopAlreadyExistError
from application.shop.gateway import ShopFilters, ShopReader, ShopSaver
from entities.shop.models import Shop, ShopId
from entities.user.models import UserId
from infrastructure.persistence.models.shop import shops_table
from infrastructure.persistence.models.user import users_table


class ShopGateway(ShopSaver, ShopReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, shop: Shop) -> None:
        self.session.add(shop)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise ShopAlreadyExistError(shop_id=shop.shop_id) from error

    async def by_id(self, shop_id: ShopId) -> Shop | None:
        query = select(Shop).where(shops_table.c.shop_id == shop_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def by_identity(self, user_id: UserId) -> Shop | None:
        query = select(Shop).select_from(
            shops_table.join(users_table, users_table.c.user_id == user_id),
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def all(
        self, filters: ShopFilters, pagination: Pagination
    ) -> list[Shop]:
        query = select(Shop)

        if filters and filters.is_active:
            query = query.where(shops_table.c.is_active)

        if pagination.order is SortOrder.ASC:
            query = query.order_by(shops_table.c.created_at.asc())
        else:
            query = query.order_by(shops_table.c.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.offset(pagination.limit)

        result = await self.session.scalars(query)

        return list(result.all())

    async def total(self, filters: ShopFilters) -> int:
        query = select(func.count(shops_table.c.shop_id))

        if filters and filters.is_active:
            query = query.where(shops_table.c.is_active)

        total: int = await self.session.scalar(query)

        return total

    async def delete(self, shop_id: ShopId) -> None:
        query = delete(Shop).where(shops_table.c.shop_id == shop_id)

        await self.session.execute(query)
