import pytest

from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.user import FakeUserGateway


@pytest.fixture
def identity_provider(
        user_id: UserId,
        user_gateway: FakeUserGateway
) -> FakeIdentityProvider:
    return FakeIdentityProvider(user_id, user_gateway)


@pytest.fixture
def commiter() -> FakeCommiter:
    return FakeCommiter()


@pytest.fixture
def webhook_manager() -> FakeWebhookManager:
    return FakeWebhookManager()
