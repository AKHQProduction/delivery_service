from delivery_service.application.errors import AuthenticationError
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.repository import StaffMemberRepository
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import RoleCollection


class TelegramIdentityProvider(IdentityProvider):
    def __init__(
        self, telegram_id: int | None, staff_repository: StaffMemberRepository
    ) -> None:
        self._telegram_id = telegram_id
        self._repository = staff_repository

    async def _current_user(self) -> StaffMember:
        if not self._telegram_id:
            raise AuthenticationError()

        if current_user := await self._repository.load_with_telegram_id(
            self._telegram_id
        ):
            return current_user
        raise AuthenticationError()

    async def get_current_user_id(self) -> UserID:
        current_user = await self._current_user()

        return current_user.entity_id

    async def get_current_staff_roles(self) -> RoleCollection:
        current_user = await self._current_user()

        return current_user.role
