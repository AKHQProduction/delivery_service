import uuid

from entities.common.tracker import Tracker
from entities.common.vo import Price
from entities.goods.models import Goods, GoodsType
from entities.goods.value_objects import GoodsTitle
from entities.shop.models import ShopId


class GoodsService:
    def __init__(self, tracker: Tracker):
        self.tracker = tracker

    def create_goods(
        self,
        shop_id: ShopId,
        title: GoodsTitle,
        price: Price,
        goods_type: GoodsType,
    ) -> Goods:
        oid = uuid.uuid4()

        new_goods = Goods(
            oid=oid,
            shop_id=shop_id,
            title=title,
            price=price,
            goods_type=goods_type,
        )

        self.tracker.add_one(new_goods)

        return new_goods

    @staticmethod
    def set_path(goods: Goods, path: str | None) -> None:
        goods.metadata_path = path

    async def delete_goods(self, goods: Goods) -> None:
        await self.tracker.delete(goods)
