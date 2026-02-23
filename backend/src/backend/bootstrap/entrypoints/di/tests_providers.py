import uuid

from dishka import WithParents, provide

from backend.application.usecases.invite_employee.interfaces import (
    GeneratedLink,
    InviteLinkGenerator,
)
from backend.bootstrap.config import AppConfig, Config
from backend.bootstrap.entrypoints.di.api_providers import (
    APIInteractorsProvider,
    AdaptersProvider,
    AuthProvider,
    GeocoderProvider,
    ServicesProvider,
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
    link_generator = provide(WithParents[FakeInviteLinkGenerator])


class MockAPIInteractorsProvider(APIInteractorsProvider):
    pass


class MockConfigProvider(ConfigProvider):
    TEST_DEBUG_USER_ID = 1000

    @provide
    def app_config(self, config: Config) -> AppConfig:
        return AppConfig(DEBUG=True, DEBUG_USER_ID=self.TEST_DEBUG_USER_ID)


class MockServicesProvider(ServicesProvider):
    pass


class MockGeocoderProvider(GeocoderProvider):
    pass


class MockAuthProvider(AuthProvider):
    pass
