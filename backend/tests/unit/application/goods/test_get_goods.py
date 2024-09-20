from uuid import UUID

import pytest

from application.goods.errors import GoodsIsNotExistError
from application.goods.interactors.get_goods import GetGoods, GetGoodsInputData
from entities.goods.models import Goods
from tests.mocks.gateways.goods import FakeGoodsGateway

fake_goods_uuid = UUID("00012f9e-f610-4ec1-8ceb-8e7f42425474")


@pytest.mark.application
@pytest.mark.goods
@pytest.mark.parametrize(
    ["goods_id", "exc_class"],
    [
        (fake_goods_uuid, None),
        (UUID("00012f9e-f610-4ea1-8ceb-8e7f42425474"), GoodsIsNotExistError),
    ],
)
async def test_get_goods(
    goods_gateway: FakeGoodsGateway, goods_id: UUID, exc_class
) -> None:
    action = GetGoods(goods_reader=goods_gateway)

    input_data = GetGoodsInputData(goods_id=goods_id)

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro
    else:
        output_data = await coro

        assert output_data
        assert isinstance(output_data, Goods)
        assert output_data.goods_id == fake_goods_uuid
