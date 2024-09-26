import pytest

from entities.shop.models import Shop, ShopId
from entities.shop.services import ShopFabric
from entities.shop.value_objects import ShopTitle, ShopToken
from entities.user.errors import UserIsNotActiveError
from entities.user.models import User, UserId
from tests.mocks.common.token_verifier import FakeTokenVerifier


@pytest.mark.entities
@pytest.mark.shop
@pytest.mark.parametrize(
    ["user_is_active", "exc_class"],
    [(True, None), (False, UserIsNotActiveError)],
)
async def test_create_shop_service(
    token_verifier: FakeTokenVerifier,
    user_is_active: bool,
    exc_class,
) -> None:
    service = ShopFabric(token_verifier)

    shop_id = ShopId(1)
    shop_title = ShopTitle("TestShop")
    shop_token = ShopToken("1234567898:AAGzbSDaSqQ-mOQEJfPLE1wBH0Y4J40xT48")

    user = User(user_id=UserId(1), full_name="Test Test Test")
    user.is_active = user_is_active

    if exc_class:
        with pytest.raises(exc_class):
            await service.create_shop(
                user=user,
                shop_id=shop_id,
                title=shop_title.title,
                token=shop_token.value,
                regular_days_off=[],
            )
    else:
        output_data = await service.create_shop(
            user=user,
            shop_id=shop_id,
            title=shop_title.title,
            token=shop_token.value,
            regular_days_off=[],
        )

        assert isinstance(output_data, Shop)
        assert token_verifier.verified
        assert user in output_data.users
