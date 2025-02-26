from uuid import UUID

import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shared.location import Location
from delivery_service.core.shared.tg_contacts import TelegramContacts
from delivery_service.core.shops.employee_collection import EmployeeCollection
from delivery_service.core.shops.shop import Shop, ShopID
from delivery_service.core.shops.value_objects import DaysOff
from delivery_service.core.users.user import User, UserID
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)


@pytest.fixture
def id_generator() -> IDGenerator:
    return IDGeneratorImpl()


@pytest.fixture
def random_user() -> User:
    return User(
        entity_id=UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cf")),
        full_name="Kevin Rudolf",
        telegram_contacts=TelegramContacts(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )


@pytest.fixture
def random_shop() -> Shop:
    return Shop(
        entity_id=ShopID(UUID("11953cdd-6dc1-797c-8029-170692b243cf")),
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
