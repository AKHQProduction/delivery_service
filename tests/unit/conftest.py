from uuid import UUID

import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shared.tg_contacts import TelegramContacts
from delivery_service.core.users.user import User, UserID
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)


@pytest.fixture
def id_generator() -> IDGenerator:
    return IDGeneratorImpl()


@pytest.fixture
def test_random_user() -> User:
    return User(
        entity_id=UserID(UUID("01953cdd-6dc1-797c-8029-170692b243cf")),
        full_name="Kevin Rudolf",
        telegram_contacts=TelegramContacts(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )
