from unittest.mock import create_autospec

from delivery_service.identity.domain.user import User
from delivery_service.shared.application.ports.idp import IdentityProvider
from delivery_service.shared.application.ports.transaction_manager import (
    TransactionManager,
)

# ruff: noqa: E501
from delivery_service.shop_managment.application.commands.create_new_shop import (
    CreateNewShopHandler,
    CreateNewShopRequest,
)
from delivery_service.shop_managment.domain.factory import (
    DaysOffData,
    ShopFactory,
)
from delivery_service.shop_managment.domain.repository import (
    ShopRepository,
)
from delivery_service.shop_managment.domain.shop import Shop


async def test_create_new_shop(random_user: User, random_shop: Shop) -> None:
    mocked_idp = create_autospec(IdentityProvider, instance=True)
    mocked_idp.get_current_user_id.return_value = random_user.entity_id
    mocked_shop_factory = create_autospec(ShopFactory, instance=True)
    mocked_shop_factory.create_shop.return_value = random_shop
    mocked_shop_repository = create_autospec(ShopRepository, instance=True)
    mocked_transaction_manager = create_autospec(
        TransactionManager, instance=True
    )

    shop_name = "My test shop"
    shop_location = "Черкаси, бул. Шевченка 30"
    days_off = DaysOffData(regular_days=[5, 6], irregular_days=[])

    request_data = CreateNewShopRequest(
        shop_name=shop_name, shop_location=shop_location, days_off=days_off
    )
    handler = CreateNewShopHandler(
        identity_provider=mocked_idp,
        shop_factory=mocked_shop_factory,
        shop_repository=mocked_shop_repository,
        transaction_manager=mocked_transaction_manager,
    )

    response_data = await handler.handle(request_data)

    mocked_idp.get_current_user_id.assert_called_once()
    mocked_shop_factory.create_shop.assert_called_once_with(
        shop_name, shop_location, days_off, random_user.entity_id
    )
    mocked_shop_repository.add.assert_called_once_with(random_shop)
    mocked_transaction_manager.commit.assert_called_once()

    assert response_data == random_shop.entity_id
    assert random_user in random_shop.employees
