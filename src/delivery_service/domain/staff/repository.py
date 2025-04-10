from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.staff_member import StaffMember


class StaffMemberRepository(Protocol):
    @abstractmethod
    def add(self, staff_member: StaffMember) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, telegram_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_telegram_id(
        self, telegram_id: int
    ) -> StaffMember | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_identity(self, user_id: UserID) -> StaffMember | None:
        raise NotImplementedError
