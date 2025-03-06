from unittest.mock import create_autospec
from uuid import UUID

import pytest

from delivery_service.identity.domain.user import User
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shared.domain.tracker import Tracker
from delivery_service.shared.domain.vo.location import Location
from delivery_service.shared.domain.vo.tg_contacts import TelegramContacts
from delivery_service.shared.infrastructure.adapters.id_generator import (
    IDGenerator,
)
from delivery_service.shop_managment.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shop_managment.domain.shop import Shop, ShopID
from delivery_service.shop_managment.domain.value_objects import DaysOff


@pytest.fixture
def id_generator() -> IDGenerator:
    return IDGenerator()


@pytest.fixture
def tracker() -> Tracker:
    return create_autospec(Tracker, instance=True)


@pytest.fixture
def random_user(tracker: Tracker) -> User:
    return User(
        entity_id=UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cf")),
        tracker=tracker,
        full_name="Kevin Rudolf",
        telegram_contacts=TelegramContacts(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )


@pytest.fixture
def random_shop(tracker: Tracker) -> Shop:
    return Shop(
        entity_id=ShopID(UUID("11953cdd-6dc1-797c-8029-170692b243cf")),
        tracker=tracker,
        owner_id=UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cf")),
        name="My test shop",
        location=Location(
            city="Черкаси",
            street="бульвар Шевченка",
            house_number="30",
            latitude=30,
            longitude=30,
        ),
        days_off=DaysOff(regular_days_off=[5, 6], irregular_days_off=[]),
        employees=EmployeeCollection(),
    )
