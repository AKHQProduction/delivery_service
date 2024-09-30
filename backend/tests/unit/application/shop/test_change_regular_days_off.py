import pytest

from application.common.access_service import AccessService
from application.errors.access import AccessDeniedError
from application.shop.errors import UserNotHaveShopError
from application.shop.interactors.change_regular_days_off import (
    ChangeRegularDaysOff,
    ChangeRegularDaysOffInputData,
)
from application.user.errors import UserNotFoundError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.shop import FakeShopGateway


@pytest.mark.application
@pytest.mark.shop
@pytest.mark.parametrize(
    ["user_id", "regular_days_off", "exc_class"],
    [
        (1, [2, 3], None),
        (10, [], UserNotFoundError),
        (2, [], UserNotHaveShopError),
        (3, [], AccessDeniedError),
    ],
)
async def test_change_regular_days_off(
    identity_provider: FakeIdentityProvider,
    shop_gateway: FakeShopGateway,
    commiter: FakeCommiter,
    access_service: AccessService,
    user_id: UserId,
    regular_days_off: list[int],
    exc_class,
) -> None:
    action = ChangeRegularDaysOff(
        identity_provider=identity_provider,
        shop_reader=shop_gateway,
        commiter=commiter,
        access_service=access_service,
    )

    input_data = ChangeRegularDaysOffInputData(
        regular_days_off=regular_days_off
    )

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro

        assert not commiter.commited
    else:
        output_data = await coro

        assert not output_data
        assert commiter.commited
