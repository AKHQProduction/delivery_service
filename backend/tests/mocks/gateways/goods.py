from decimal import Decimal
from uuid import UUID

from application.commands.goods import (
    GoodsSaver,
)
from application.common.errors import GoodsAlreadyExistsError
from application.common.persistence import (
    GoodsGateway,
    GoodsReaderFilters,
    Pagination,
)
from entities.common.vo import Price
from entities.goods.models import Goods, GoodsId, GoodsType
from entities.goods.value_objects import GoodsTitle
from entities.shop.models import ShopId

fake_goods_uuid = UUID("00012f9e-f610-4ec1-8ceb-8e7f42425474")


class FakeGoodsGateway(GoodsSaver, GoodsGateway):
    def __init__(self):
        self.goods: dict[UUID, Goods] = {
            fake_goods_uuid: Goods(
                goods_id=GoodsId(fake_goods_uuid),
                shop_id=ShopId(1234567898),
                title=GoodsTitle("Test Goods"),
                price=Price(Decimal("2.50")),
                goods_type=GoodsType.OTHER,
                metadata_path=f"1234567898/{fake_goods_uuid}.jpg",
            )
        }

        self.saved = False
        self.deleted = False

    async def save(self, goods: Goods) -> None:
        goods_in_memory = await self.load_with_id(goods_id=goods.goods_id)

        if goods_in_memory:
            raise GoodsAlreadyExistsError(goods_id=goods.goods_id)

        self.goods[goods.goods_id] = goods

    async def load_with_id(self, goods_id: GoodsId) -> Goods | None:
        return self.goods.get(goods_id, None)

    async def load_many(
        self, filters: GoodsReaderFilters, pagination: Pagination
    ) -> list[Goods]:
        return list(self.goods.values())

    async def total(self, filters: GoodsReaderFilters) -> int:
        return len(list(self.goods.values()))

    async def delete(self, goods: Goods) -> None:
        goods = await self.load_with_id(goods_id=goods.goods_id)

        if goods:
            del self.goods[goods.goods_id]

        self.deleted = True
