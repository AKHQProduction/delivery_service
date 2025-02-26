from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.application.ports.view_manager import ViewManager
from delivery_service.core.users.errors import UserAlreadyExistsError
from delivery_service.core.users.factory import (
    TelegramContactsData,
    UserFactory,
)
from delivery_service.core.users.repository import UserRepository


@dataclass(frozen=True)
class MainBotStartRequest(Request[None]):
    full_name: str
    telegram_data: TelegramContactsData


class MainBotStartHandler(RequestHandler[MainBotStartRequest, None]):
    def __init__(
        self,
        user_repository: UserRepository,
        user_factory: UserFactory,
        view_manager: ViewManager,
        transaction_manager: TransactionManager,
    ) -> None:
        self._repository = user_repository
        self._factory = user_factory
        self._view_manager = view_manager
        self._transaction_manager = transaction_manager

    async def handle(self, request: MainBotStartRequest) -> None:
        try:
            new_service_user = await self._factory.create_user(
                full_name=request.full_name,
                telegram_contacts_data=request.telegram_data,
            )
        except UserAlreadyExistsError:
            await self._view_manager.send_greeting_message()
        else:
            self._repository.add(new_service_user)
            await self._transaction_manager.commit()
            await self._view_manager.send_greeting_message()
