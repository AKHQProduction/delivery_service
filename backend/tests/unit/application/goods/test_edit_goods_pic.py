from uuid import UUID

import pytest

from application.common.access_service import AccessService
from application.goods.input_data import FileMetadata
from application.goods.interactors.edit_goods import (
    EditGoods,
    EditGoodsInputData,
)
from entities.goods.models import GoodsId
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
    ["user_id", "goods_id", "payload", "exc_class"],
    [(1, fake_goods_uuid, None, None)],
)
async def test_edit_goods_pic(
    identity_provider: FakeIdentityProvider,
    access_service: AccessService,
    shop_gateway: FakeShopGateway,
    goods_gateway: FakeGoodsGateway,
    file_manager: FakeFileManager,
    commiter: FakeCommiter,
    user_id: UserId,
    goods_id: GoodsId,
    payload: bytes | None,
    exc_class,
) -> None:
    action = EditGoods(
        identity_provider=identity_provider,
        access_service=access_service,
        shop_reader=shop_gateway,
        goods_reader=goods_gateway,
        file_manager=file_manager,
        commiter=commiter,
    )

    input_payload = FileMetadata(payload) if payload else None

    input_data = EditGoodsInputData(goods_id=goods_id, metadata=input_payload)

    coro = action(input_data)

    output_data = await coro

    assert not output_data
    assert file_manager.saved or file_manager.deleted
