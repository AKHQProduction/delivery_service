import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.shop.errors import UserNotHaveShopError
from application.shop.interactors.resume_shop import ResumeShop
from application.user.errors import UserIsNotExistError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.shop import FakeShopGateway


@pytest.mark.application
@pytest.mark.shop
@pytest.mark.parametrize(
    ["user_id", "shop_id", "exc_class"],
    [
        (1, 1234567898, None),
        (4, 9876543212, UserIsNotExistError),
        (3, 1234567898, AccessDeniedError),
        (2, 1234567898, UserNotHaveShopError),
    ],
)
async def test_resume_shop(
    shop_gateway: FakeShopGateway,
    identity_provider: FakeIdentityProvider,
    webhook_manager: FakeWebhookManager,
    commiter: FakeCommiter,
    access_service: AccessService,
    user_id: UserId,
    shop_id: int,
    exc_class,
) -> None:
    action = ResumeShop(
        shop_reader=shop_gateway,
        identity_provider=identity_provider,
        webhook_manager=webhook_manager,
        commiter=commiter,
        access_service=access_service,
    )

    coro = action()

    if exc_class:
        with pytest.raises(exc_class):
            await coro

        assert not commiter.commited
        assert not webhook_manager.setup

    else:
        output_data = await coro

        assert not output_data

        assert commiter.commited
        assert not webhook_manager.dropped
        assert webhook_manager.setup
        assert shop_id in shop_gateway.shops
