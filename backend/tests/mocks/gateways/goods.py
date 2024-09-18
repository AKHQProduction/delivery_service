from decimal import Decimal
from uuid import UUID

from application.goods.errors import GoodsAlreadyExistError
from application.goods.gateway import GoodsReader, GoodsSaver
from entities.goods.models import Goods, GoodsId
from entities.goods.value_objects import GoodsPrice, GoodsTitle
from entities.shop.models import ShopId

fake_goods_uuid = UUID("00012f9e-f610-4ec1-8ceb-8e7f42425474")


class FakeGoodsGateway(GoodsSaver, GoodsReader):
    def __init__(self):
        self.goods: dict[UUID, Goods] = {
            fake_goods_uuid: Goods(
                goods_id=GoodsId(fake_goods_uuid),
                shop_id=ShopId(1234567898),
                title=GoodsTitle("Test Goods"),
                price=GoodsPrice(Decimal("2.50")),
            )
        }

        self.saved = False
        self.deleted = False

    async def save(self, goods: Goods) -> None:
        goods_in_memory = await self.by_id(goods_id=goods.goods_id)

        if goods_in_memory:
            raise GoodsAlreadyExistError(goods_id=goods.goods_id)

        self.goods[goods.goods_id] = goods

    async def by_id(self, goods_id: GoodsId) -> Goods | None:
        return self.goods.get(goods_id, None)

    async def delete(self, goods: Goods) -> None:
        goods = await self.by_id(goods_id=goods.goods_id)

        if goods:
            del self.goods[goods.goods_id]

        self.deleted = True
