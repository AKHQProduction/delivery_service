from decimal import Decimal
from io import BytesIO
from uuid import UUID

import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.goods.interactors.add_goods import (
    AddGoods,
    AddGoodsInputData,
    FileMetadata,
)
from application.shop.errors import UserNotHaveShopError
from application.user.errors import UserIsNotExistError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.file_manager import FakeFileManager
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.goods import FakeGoodsGateway
from tests.mocks.gateways.shop import FakeShopGateway


@pytest.mark.application
@pytest.mark.goods
@pytest.mark.parametrize(
    ["user_id", "title", "price", "payload", "exc_class"],
    [
        (1, "New Test Goods", "10.00", BytesIO(b"test"), None),
        (4, "New Test Goods", "10.00", BytesIO(b"test"), UserIsNotExistError),
        (2, "New Test Goods", "10.00", BytesIO(b"test"), UserNotHaveShopError),
        (3, "New Test Goods", "10.00", BytesIO(b"test"), AccessDeniedError),
    ],
)
async def test_add_goods(
    identity_provider: FakeIdentityProvider,
    access_service: AccessService,
    shop_gateway: FakeShopGateway,
    goods_gateway: FakeGoodsGateway,
    file_manager: FakeFileManager,
    commiter: FakeCommiter,
    user_id: UserId,
    title: str,
    price: Decimal,
    payload: bytes,
    exc_class,
) -> None:
    start_length_goods_in_memory = len(goods_gateway.goods)

    action = AddGoods(
        identity_provider=identity_provider,
        access_service=access_service,
        shop_reader=shop_gateway,
        goods_saver=goods_gateway,
        file_manager=file_manager,
        commiter=commiter,
    )

    input_data = AddGoodsInputData(
        title=title,
        price=price,
        metadata=FileMetadata(payload) if payload else None,
    )

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro
    else:
        output_data = await coro

        assert output_data
        assert isinstance(output_data, UUID)

        assert len(goods_gateway.goods) == start_length_goods_in_memory + 1
        assert file_manager.saved
        assert commiter.commited
