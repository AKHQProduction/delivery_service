from abc import abstractmethod
from typing import Protocol

from delivery_service.application.common.dto import TelegramContactsData


class SocialNetworkChecker(Protocol):
    @abstractmethod
    async def check_telegram_data(
        self, telegram_id: int
    ) -> TelegramContactsData | None:
        raise NotImplementedError
