from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.application.errors import StaffMemberAlreadyExistsError
from delivery_service.application.ports.view_manager import (
    ViewManager,
)
from delivery_service.domain.staff.factory import (
    StaffMemberFactory,
    TelegramContactsData,
)
from delivery_service.domain.staff.repository import StaffMemberRepository


@dataclass(frozen=True)
class BotStartRequest(Request[None]):
    full_name: str
    telegram_data: TelegramContactsData


class BotStartHandler(RequestHandler[BotStartRequest, None]):
    def __init__(
        self,
        staff_member_repository: StaffMemberRepository,
        staff_member_factory: StaffMemberFactory,
        view_manager: ViewManager,
    ) -> None:
        self._repository = staff_member_repository
        self._factory = staff_member_factory
        self._view_manager = view_manager

    async def handle(self, request: BotStartRequest) -> None:
        try:
            new_service_user = await self._factory.create_staff_member(
                full_name=request.full_name,
                telegram_contacts_data=request.telegram_data,
            )
        except StaffMemberAlreadyExistsError:
            return None
        else:
            return self._repository.add(new_service_user)
