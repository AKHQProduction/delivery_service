from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from delivery_service.domain.staff.staff_member import StaffMember


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None


class StaffMemberFactory(Protocol):
    @abstractmethod
    async def create_staff_member(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData,
    ) -> StaffMember: ...
