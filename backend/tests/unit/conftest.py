import pytest

from application.common.access_service import AccessService
from entities.user.models import UserId
from infrastructure.tg.config import ProjectConfig
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.file_manager import FakeFileManager
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.common.webhook_manager import FakeWebhookManager
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.goods import FakeGoodsGateway
from tests.mocks.gateways.profile import FakeProfileGateway
from tests.mocks.gateways.shop import FakeShopGateway
from tests.mocks.gateways.user import FakeUserGateway


@pytest.fixture
def identity_provider(
    user_id: UserId,
    user_gateway: FakeUserGateway,
    employee_gateway: FakeEmployeeGateway,
) -> FakeIdentityProvider:
    return FakeIdentityProvider(user_id, user_gateway, employee_gateway)


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
def project_config() -> ProjectConfig:
    return ProjectConfig(admin_id=1)


@pytest.fixture
def access_service(
    employee_gateway: FakeEmployeeGateway, project_config: ProjectConfig
) -> AccessService:
    return AccessService(
        employee_reader=employee_gateway, project_config=project_config
    )


@pytest.fixture
def goods_gateway() -> FakeGoodsGateway:
    return FakeGoodsGateway()


@pytest.fixture
def file_manager() -> FakeFileManager:
    return FakeFileManager()


@pytest.fixture
def profile_gateway() -> FakeProfileGateway:
    return FakeProfileGateway()
