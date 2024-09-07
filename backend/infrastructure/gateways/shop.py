from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.shop.errors import (
    ShopAlreadyExistError
)
from application.shop.gateway import ShopReader, ShopSaver
from entities.shop.models import Shop, ShopId
from infrastructure.persistence.models.shop import shops_table


class InMemoryShopGateway(ShopSaver, ShopReader):
    def __init__(self):
        self._shops: dict[int, Shop] = {}

    async def by_id(self, shop_id: ShopId) -> Shop | None:
        return self._shops.get(shop_id)

    async def save(self, shop: Shop) -> None:
        self._shops[shop.shop_id] = shop

    async def update(self, shop: Shop) -> None:
        self._shops[shop.shop_id] = shop


class ShopGateway(ShopSaver, ShopReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, shop: Shop) -> None:
        self.session.add(shop)

        try:
            await self.session.flush()
        except IntegrityError:
            raise ShopAlreadyExistError(shop_id=shop.shop_id)

    async def by_id(self, shop_id: ShopId) -> Shop | None:
        query = select(Shop).where(shops_table.c.shop_id == shop_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()
