from uuid import UUID

import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.goods.errors import GoodsIsNotExistError
from application.goods.interactors.delete_goods import (
    DeleteGoods,
    DeleteGoodsInputData,
)
from application.shop.errors import UserNotHaveShopError
from application.user.errors import UserIsNotExistError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.file_manager import FakeFileManager
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.goods import FakeGoodsGateway
from tests.mocks.gateways.shop import FakeShopGateway

fake_goods_uuid = UUID("00012f9e-f610-4ec1-8ceb-8e7f42425474")


@pytest.mark.application
@pytest.mark.goods
@pytest.mark.parametrize(
    ["user_id", "goods_id", "exc_class"],
    [
        (1, fake_goods_uuid, None),
        (4, fake_goods_uuid, UserIsNotExistError),
        (2, fake_goods_uuid, UserNotHaveShopError),
        (3, fake_goods_uuid, AccessDeniedError),
        (
            1,
            UUID("00012f9e-f610-4bb1-8ceb-8e7f42425474"),
            GoodsIsNotExistError,
        ),
    ],
)
async def test_delete_goods(
    identity_provider: FakeIdentityProvider,
    access_service: AccessService,
    shop_gateway: FakeShopGateway,
    goods_gateway: FakeGoodsGateway,
    file_manager: FakeFileManager,
    commiter: FakeCommiter,
    user_id: UserId,
    goods_id: UUID,
    exc_class,
) -> None:
    start_length_goods_in_memory = len(goods_gateway.goods)

    action = DeleteGoods(
        identity_provider=identity_provider,
        access_service=access_service,
        shop_reader=shop_gateway,
        goods_saver=goods_gateway,
        goods_reader=goods_gateway,
        file_manager=file_manager,
        commiter=commiter,
    )

    input_data = DeleteGoodsInputData(goods_id)

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro
        assert len(goods_gateway.goods)
        assert not file_manager.deleted
        assert not commiter.commited

    else:
        output_data = await coro

        assert not output_data
        assert len(goods_gateway.goods) == start_length_goods_in_memory - 1
        assert file_manager.deleted
        assert commiter.commited
