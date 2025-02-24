import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.users.factory import ServiceClientFactory
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)
from delivery_service.infrastructure.factories.service_client_factory import (
    ServiceClientFactoryImpl,
)


@pytest.fixture
def id_generator() -> IDGenerator:
    return IDGeneratorImpl()


@pytest.fixture
def service_client_factory(id_generator: IDGenerator) -> ServiceClientFactory:
    return ServiceClientFactoryImpl(id_generator=id_generator)
