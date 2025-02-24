import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.users.factory import UserFactory
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)
from delivery_service.infrastructure.factories.user_factory import (
    UserFactoryImpl,
)


@pytest.fixture
def id_generator() -> IDGenerator:
    return IDGeneratorImpl()


@pytest.fixture
def service_user_factory(id_generator: IDGenerator) -> UserFactory:
    return UserFactoryImpl(id_generator=id_generator)
