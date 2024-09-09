import pytest

from entities.user.models import User
from tests.mocks.gateways.user import FakeUserGateway


@pytest.fixture
def user_gateway(user: User) -> FakeUserGateway:
    return FakeUserGateway(user)
