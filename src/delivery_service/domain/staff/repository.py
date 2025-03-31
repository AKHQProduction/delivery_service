from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.staff.factory import TelegramContactsData
from delivery_service.domain.staff.staff_member import StaffMember


class StaffMemberRepository(Protocol):
    @abstractmethod
    def add(self, staff_member: StaffMember) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, telegram_data: TelegramContactsData) -> bool:
        raise NotImplementedError
