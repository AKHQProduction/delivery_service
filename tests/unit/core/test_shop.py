from datetime import date
from typing import Type
from unittest.mock import create_autospec

import pytest

from delivery_service.identity.domain.user import User
from delivery_service.shared.domain.vo.location import Location
from delivery_service.shared.infrastructure.adapters.id_generator import (
    IDGenerator,
)
from delivery_service.shared.infrastructure.integration.geopy.geolocator import (  # noqa: E501
    Geolocator,
)
from delivery_service.shop_managment.domain.errors import (
    InvalidDayOfWeekError,
    ShopCreationNotAllowedError,
)
from delivery_service.shop_managment.domain.factory import DaysOffData
from delivery_service.shop_managment.domain.shop import Shop
from delivery_service.shop_managment.infrastructure.shop_factory import (
    ShopFactoryImpl,
)


async def test_successfully_create_shop(
    id_generator: IDGenerator, random_user: User
) -> None:
    shop_name = "New test shop"
    shop_location = "Черкассы, улица Шевченка 228"
    shop_days_off = DaysOffData(regular_days=[5, 6], irregular_days=[])

    mock_geolocator = create_autospec(Geolocator, instance=True)
    mock_geolocator.get_location_data.return_value = Location(
        city="Черкаси",
        street="вулиця Шевченка",
        house_number="228",
        latitude=123.0,
        longitude=123.0,
    )

    shop_factory = ShopFactoryImpl(
        id_generator=id_generator, geolocator=mock_geolocator
    )

    new_shop = await shop_factory.create_shop(
        shop_name=shop_name,
        shop_location=shop_location,
        shop_days_off=shop_days_off,
        user=random_user,
    )

    assert isinstance(new_shop, Shop)

    assert new_shop.name == shop_name
    assert new_shop.location == "Черкаси, вулиця Шевченка 228"
    assert new_shop.location_coordinates == (123.0, 123.0)
    assert new_shop.regular_days_off == [5, 6]
    assert new_shop.irregular_days_off == []


@pytest.mark.skip
async def test_unsuccessfully_create_shop_when_user_already_employee(
    random_user: User, id_generator: IDGenerator
) -> None:
    shop_name = "New test shop"
    shop_location = "Черкассы, улица Шевченка 228"
    shop_days_off = DaysOffData(regular_days=[5, 6], irregular_days=[])

    mocked_user = create_autospec(User, instance=True)

    mock_geolocator = create_autospec(Geolocator, instance=True)

    shop_factory = ShopFactoryImpl(
        id_generator=id_generator, geolocator=mock_geolocator
    )

    with pytest.raises(ShopCreationNotAllowedError):
        await shop_factory.create_shop(
            shop_name=shop_name,
            shop_location=shop_location,
            shop_days_off=shop_days_off,
            user=mocked_user,
        )


@pytest.mark.parametrize(
    ["days", "exception"],
    [
        ([1, 2], None),
        ([-1, 2], InvalidDayOfWeekError),
        ([8, 2], InvalidDayOfWeekError),
    ],
)
def test_successfully_edit_shop_regular_days_off(
    random_shop: Shop, days: list[int], exception: Type[Exception] | None
) -> None:
    if exception:
        with pytest.raises(exception):
            random_shop.edit_regular_days_off(days)
    else:
        random_shop.edit_regular_days_off(days)
        assert random_shop.regular_days_off == days


@pytest.mark.parametrize(["day"], [(date(2025, 2, 26),)])
def test_can_deliver_in_this_day(random_shop: Shop, day: date) -> None:
    assert random_shop.can_deliver_in_this_day(day) is True


@pytest.mark.parametrize(["day"], [(date(2025, 2, 1),)])
def test_cannot_deliver_in_this_day(random_shop: Shop, day: date) -> None:
    assert random_shop.can_deliver_in_this_day(day) is False
