from dishka import provide

from backend.bootstrap.config import AppConfig, Config
from backend.bootstrap.entrypoints.di.api_providers import WebAppProvider
from backend.bootstrap.entrypoints.di.common import (
    ConfigProvider,
)


class MockConfigProvider(ConfigProvider):
    @provide
    def app_config(self, config: Config) -> AppConfig:
        return AppConfig(DEBUG=True)


class MockWebAppProvider(WebAppProvider):
    pass
