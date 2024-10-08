import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.shop.errors import ShopAlreadyExistError
from application.shop.interactors.create_shop import (
    CreateShop,
    CreateShopInputData,
)
from application.user.errors import UserNotFoundError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.profile import FakeProfileGateway
from tests.mocks.gateways.shop import FakeShopGateway
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.shop
@pytest.mark.parametrize(
    ["user_id", "shop_id", "exc_class"],
    [
        (2, 9876543212, None),
        (4, 9876543212, UserNotFoundError),
        (1, 9876543212, AccessDeniedError),
        (2, 1234567898, ShopAlreadyExistError),
    ],
)
async def test_create_shop(
    shop_gateway: FakeShopGateway,
    user_gateway: FakeUserGateway,
    employee_gateway: FakeEmployeeGateway,
    identity_provider: FakeIdentityProvider,
    webhook_manager: FakeWebhookManager,
    commiter: FakeCommiter,
    access_service: AccessService,
    profile_gateway: FakeProfileGateway,
    user_id: UserId,
    shop_id: int,
    exc_class,
) -> None:
    shop_title = "TestShop"
    shop_token = f"{shop_id}:AAGzbSDaSqQ-mOQEJfPLE1wBH0Y4J40xT48"
    delivery_distance = 50
    location = (48.5035903, 31.0787222)

    action = CreateShop(
        user_saver=user_gateway,
        shop_saver=shop_gateway,
        employee_saver=employee_gateway,
        identity_provider=identity_provider,
        webhook_manager=webhook_manager,
        commiter=commiter,
        access_service=access_service,
        profile_reader=profile_gateway,
    )

    input_data = CreateShopInputData(
        token=shop_token,
        title=shop_title,
        delivery_distance=delivery_distance,
        location=location,
    )

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro

        assert not commiter.commited
        assert not employee_gateway.saved
        assert not shop_gateway.saved

    else:
        output_data = await coro

        assert output_data
        assert isinstance(output_data, int)

        assert output_data == shop_id

        assert commiter.commited
        assert employee_gateway.saved
        assert shop_gateway.saved
        assert webhook_manager.setup
        assert shop_id in shop_gateway.shops
