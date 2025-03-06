from datetime import date
from typing import Type
from unittest.mock import create_autospec
from uuid import UUID

import pytest

from delivery_service.identity.domain.user import User
from delivery_service.shared.domain.employee import (
    Employee,
    EmployeeRole,
)
from delivery_service.shared.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shared.domain.shop_id import ShopID
from delivery_service.shared.domain.vo.location import Location
from delivery_service.shared.infrastructure.adapters.id_generator import (
    IDGenerator,
)
from delivery_service.shared.infrastructure.integration.geopy.geolocator import (  # noqa: E501
    Geolocator,
)
from delivery_service.shop_management.domain.errors import (
    InvalidDayOfWeekError,
    ShopCreationNotAllowedError,
)
from delivery_service.shop_management.domain.factory import DaysOffData
from delivery_service.shop_management.domain.repository import (
    ShopRepository,
)
from delivery_service.shop_management.domain.shop import Shop
from delivery_service.shop_management.domain.value_objects import DaysOff
from delivery_service.shop_management.infrastructure.shop_factory import (
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

    mock_shop_repository = create_autospec(ShopRepository, instance=True)
    mock_shop_repository.exists.return_value = False

    shop_factory = ShopFactoryImpl(
        id_generator=id_generator,
        geolocator=mock_geolocator,
        shop_repository=mock_shop_repository,
    )

    new_shop = await shop_factory.create_shop(
        shop_name=shop_name,
        shop_location=shop_location,
        shop_days_off=shop_days_off,
        identity_id=random_user.entity_id,
    )

    assert isinstance(new_shop, Shop)

    assert new_shop.name == shop_name
    assert new_shop.location == "Черкаси, вулиця Шевченка 228"
    assert new_shop.location_coordinates == (123.0, 123.0)
    assert new_shop.regular_days_off == [5, 6]
    assert new_shop.irregular_days_off == []


async def test_unsuccessfully_create_shop_when_user_already_employee(
    random_user: User, id_generator: IDGenerator
) -> None:
    shop_name = "New test shop"
    shop_location = "Черкассы, улица Шевченка 228"
    shop_days_off = DaysOffData(regular_days=[5, 6], irregular_days=[])

    mocked_user = create_autospec(User, instance=True)

    mock_geolocator = create_autospec(Geolocator, instance=True)

    mock_shop_repository = create_autospec(ShopRepository, instance=True)
    mock_shop_repository.exists.return_value = True

    shop_factory = ShopFactoryImpl(
        id_generator=id_generator,
        geolocator=mock_geolocator,
        shop_repository=mock_shop_repository,
    )

    with pytest.raises(ShopCreationNotAllowedError):
        await shop_factory.create_shop(
            shop_name=shop_name,
            shop_location=shop_location,
            shop_days_off=shop_days_off,
            identity_id=mocked_user.entity_id,
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


async def test_discard_from_employee() -> None:
    # GIVEN
    owner_id = UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cf"))
    employee_id = UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cc"))
    candidate_to_fire = Employee(
        employee_id=employee_id,
        role=EmployeeRole.SHOP_MANAGER,
    )

    employees = EmployeeCollection(
        {
            Employee(
                employee_id=owner_id,
                role=EmployeeRole.SHOP_OWNER,
            ),
            candidate_to_fire,
        }
    )
    shop = Shop(
        entity_id=ShopID(UUID("11953cdd-6dc1-797c-8029-170692b243cf")),
        owner_id=owner_id,
        name="My test shop",
        location=Location(
            city="Черкаси",
            street="бульвар Шевченка",
            house_number="30",
            latitude=30,
            longitude=30,
        ),
        days_off=DaysOff(regular_days_off=[5, 6], irregular_days_off=[]),
        employees=employees,
    )

    # WHEN
    shop.discard_employee(employee=candidate_to_fire, firer_id=owner_id)

    # THEN
    assert candidate_to_fire not in shop.employees


def test_add_new_employee() -> None:
    # GIVEN
    owner_id = UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cf"))
    employee_id = UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cc"))

    employees = EmployeeCollection(
        {
            Employee(
                employee_id=owner_id,
                role=EmployeeRole.SHOP_OWNER,
            )
        }
    )
    shop = Shop(
        entity_id=ShopID(UUID("11953cdd-6dc1-797c-8029-170692b243cf")),
        owner_id=owner_id,
        name="My test shop",
        location=Location(
            city="Черкаси",
            street="бульвар Шевченка",
            house_number="30",
            latitude=30,
            longitude=30,
        ),
        days_off=DaysOff(regular_days_off=[5, 6], irregular_days_off=[]),
        employees=employees,
    )

    # WHEN
    shop.add_employee(
        employee_id=employee_id,
        role=EmployeeRole.SHOP_MANAGER,
        hirer_id=owner_id,
    )

    # THEN
    new_employee = Employee(
        employee_id=employee_id,
        role=EmployeeRole.SHOP_MANAGER,
    )
    assert new_employee in shop.employees
