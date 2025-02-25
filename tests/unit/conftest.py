import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)


@pytest.fixture
def id_generator() -> IDGenerator:
    return IDGeneratorImpl()
