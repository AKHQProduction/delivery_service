from delivery_service.application.ports.social_network_provider import (
    SocialNetworkProvider,
)


class SocialNetworkProviderImpl(SocialNetworkProvider):
    def __init__(self, telegram_id: int | None) -> None:
        self._telegram_id = telegram_id

    async def get_telegram_id(self) -> int | None:
        return self._telegram_id
