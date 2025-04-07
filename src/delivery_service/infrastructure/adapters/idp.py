from delivery_service.application.errors import AuthenticationError
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.repository import StaffMemberRepository
from delivery_service.domain.staff.staff_role import RoleCollection
from delivery_service.domain.user.repository import ServiceUserRepository


class TelegramIdentityProvider(IdentityProvider):
    def __init__(
        self,
        telegram_id: int | None,
        service_user_repository: ServiceUserRepository,
        staff_member_repository: StaffMemberRepository,
    ) -> None:
        self._telegram_id = telegram_id
        self._repository = service_user_repository
        self._staff_member_repository = staff_member_repository

    async def get_current_user_id(self) -> UserID:
        if not self._telegram_id:
            raise AuthenticationError()

        if current_user := await self._repository.load_with_social_network(
            self._telegram_id
        ):
            return current_user.entity_id
        raise AuthenticationError()

    async def get_current_staff_roles(self) -> RoleCollection | None:
        if not self._telegram_id:
            raise AuthenticationError()

        if (
            current_user
            := await self._staff_member_repository.load_with_telegram_id(
                self._telegram_id
            )
        ):
            return current_user.roles
        return None
