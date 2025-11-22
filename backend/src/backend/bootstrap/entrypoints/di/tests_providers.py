import uuid

from dishka import provide

from backend.application.usecases.invite_employee.interfaces import (
    GeneratedLink,
    InviteLinkGenerator,
)
from backend.bootstrap.config import AppConfig, Config
from backend.bootstrap.entrypoints.di.api_providers import (
    APIInteractorsProvider,
    AdaptersProvider,
    WebAppProvider,
)
from backend.bootstrap.entrypoints.di.common import (
    ConfigProvider,
)


class FakeInviteLinkGenerator(InviteLinkGenerator):
    async def generate(self) -> GeneratedLink:
        payload = f"invite_link_{uuid.uuid4()}"
        link = f"https://t.me/test_bot?start={payload}"
        return GeneratedLink(link=link, payload=payload)


class MockAdaptersProvider(AdaptersProvider):
    pass


class MockAPIInteractorsProvider(APIInteractorsProvider):
    pass


class MockConfigProvider(ConfigProvider):
    @provide
    def app_config(self, config: Config) -> AppConfig:
        return AppConfig(DEBUG=True)


class MockWebAppProvider(WebAppProvider):
    pass
