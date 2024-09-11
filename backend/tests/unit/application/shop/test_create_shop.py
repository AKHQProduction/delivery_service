import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.shop.errors import ShopAlreadyExistError
from application.shop.interactors.create_shop import (
    CreateShop,
    CreateShopInputData
)
from application.user.errors import UserIsNotExistError
from entities.shop.services import ShopService
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.token_verifier import FakeTokenVerifier
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.shop import FakeShopGateway
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.shop
@pytest.mark.parametrize(
        ["user_id", "shop_id", "exc_class"],
        [
            (2, 9876543212, None),
            (4, 9876543212, UserIsNotExistError),
            (1, 9876543212, AccessDeniedError),
            (2, 1234567898, ShopAlreadyExistError)
        ]
)
async def test_create_shop(
        shop_gateway: FakeShopGateway,
        user_gateway: FakeUserGateway,
        employee_gateway: FakeEmployeeGateway,
        identity_provider: FakeIdentityProvider,
        token_verifier: FakeTokenVerifier,
        webhook_manager: FakeWebhookManager,
        commiter: FakeCommiter,
        access_service: AccessService,
        user_id: UserId,
        shop_id: int,
        exc_class
) -> None:
    shop_service = ShopService(token_verifier)

    shop_title = "TestShop"
    shop_token = "9876543212:AAGzbSDaSqQ-mOQEJfPLE1wBH0Y4J40xT48"

    action = CreateShop(
            user_saver=user_gateway,
            shop_saver=shop_gateway,
            employee_saver=employee_gateway,
            identity_provider=identity_provider,
            webhook_manager=webhook_manager,
            commiter=commiter,
            access_service=access_service,
            shop_service=shop_service
    )

    input_data = CreateShopInputData(
            shop_id=shop_id,
            token=shop_token,
            title=shop_title
    )

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro

        assert not commiter.commited
        assert not employee_gateway.saved
        assert not shop_gateway.saved
        assert not webhook_manager.setup

    else:
        output_data = await coro

        assert output_data
        assert isinstance(output_data, int)

        assert output_data == shop_id

        assert commiter.commited
        assert employee_gateway.saved
        assert shop_gateway.saved
        assert webhook_manager.setup
        assert shop_id in shop_gateway.shops.keys()
