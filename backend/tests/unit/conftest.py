import pytest

from application.common.access_service import AccessService
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.token_verifier import FakeTokenVerifier
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.shop import FakeShopGateway
from tests.mocks.gateways.user import FakeUserGateway


@pytest.fixture
def token_verifier() -> FakeTokenVerifier:
    return FakeTokenVerifier()


@pytest.fixture
def identity_provider(
    user_id: UserId,
    user_gateway: FakeUserGateway,
) -> FakeIdentityProvider:
    return FakeIdentityProvider(user_id, user_gateway)


@pytest.fixture
def commiter() -> FakeCommiter:
    return FakeCommiter()


@pytest.fixture
def webhook_manager() -> FakeWebhookManager:
    return FakeWebhookManager()


@pytest.fixture
def employee_gateway() -> FakeEmployeeGateway:
    return FakeEmployeeGateway()


@pytest.fixture
def shop_gateway() -> FakeShopGateway:
    return FakeShopGateway()


@pytest.fixture
def user_gateway() -> FakeUserGateway:
    return FakeUserGateway()


@pytest.fixture
def access_service(
    employee_gateway: FakeEmployeeGateway,
    identity_provider: FakeIdentityProvider,
) -> AccessService:
    return AccessService(
        employee_reader=employee_gateway,
        identity_provider=identity_provider,
    )
