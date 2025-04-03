from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from delivery_service.domain.staff.staff_member import StaffMember


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None


class StaffMemberRepository(Protocol):
    @abstractmethod
    def add(self, staff_member: StaffMember) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, telegram_data: TelegramContactsData) -> bool:
        raise NotImplementedError
