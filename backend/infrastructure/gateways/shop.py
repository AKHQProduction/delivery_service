from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.shop.errors import ShopAlreadyExistError
from application.shop.gateway import ShopReader, ShopSaver
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

    async def delete(self, shop_id: ShopId) -> None:
        query = delete(Shop).where(shops_table.c.shop_id == shop_id)

        await self.session.execute(query)
