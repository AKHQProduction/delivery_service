import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.shop.errors import UserNotHaveShopError
from application.shop.interactors.delete_shop import DeleteShop
from application.user.errors import UserNotFoundError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.file_manager import FakeFileManager
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.shop import FakeShopGateway


@pytest.mark.application
@pytest.mark.shop
@pytest.mark.parametrize(
    ["user_id", "shop_id", "exc_class"],
    [
        (1, 1234567898, None),
        (4, 9876543212, UserNotFoundError),
        (3, 1234567898, AccessDeniedError),
        (2, 1234567898, UserNotHaveShopError),
    ],
)
async def test_delete_shop(
    shop_gateway: FakeShopGateway,
    identity_provider: FakeIdentityProvider,
    webhook_manager: FakeWebhookManager,
    commiter: FakeCommiter,
    access_service: AccessService,
    file_manager: FakeFileManager,
    user_id: UserId,
    shop_id: int,
    exc_class,
) -> None:
    action = DeleteShop(
        shop_saver=shop_gateway,
        shop_reader=shop_gateway,
        identity_provider=identity_provider,
        webhook_manager=webhook_manager,
        file_manager=file_manager,
        commiter=commiter,
        access_service=access_service,
    )

    coro = action()

    if exc_class:
        with pytest.raises(exc_class):
            await coro

        assert not commiter.commited
        assert not shop_gateway.deleted
        assert not webhook_manager.dropped
        assert not file_manager.deleted

    else:
        output_data = await coro

        assert not output_data

        assert commiter.commited
        assert shop_gateway.deleted
        assert webhook_manager.dropped
        assert shop_id not in shop_gateway.shops
        assert file_manager.deleted
