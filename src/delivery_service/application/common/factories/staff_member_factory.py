from typing import Final, cast

from delivery_service.application.errors import StaffMemberAlreadyExistsError
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.shared.vo.tg_contacts import TelegramContacts
from delivery_service.domain.staff.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
)
from delivery_service.domain.staff.repository import (
    StaffMemberRepository,
    TelegramContactsData,
)
from delivery_service.domain.staff.role_repository import RoleRepository
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import (
    Role,
    RoleCollection,
    StaffRole,
    StaffRoleID,
)


class StaffMemberFactory:
    _MIN_FULLNAME_LENGTH: Final[int] = 1
    _MAX_FULLNAME_LENGTH: Final[int] = 128

    def __init__(
        self,
        id_generator: IDGenerator,
        staff_member_repository: StaffMemberRepository,
        role_repository: RoleRepository,
    ) -> None:
        self._id_generator = id_generator
        self._user_repository = staff_member_repository
        self._role_repository = role_repository

    async def create_staff_member(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData,
    ) -> StaffMember:
        self._validate(full_name)

        if not await self._user_repository.exists(
            telegram_data=telegram_contacts_data
        ):
            user_id = self._id_generator.generate_user_id()
            return StaffMember(
                entity_id=user_id,
                full_name=full_name,
                roles=RoleCollection(roles=await self._get_user_role()),
                telegram_contacts=TelegramContacts(
                    _user_id=user_id,
                    telegram_id=telegram_contacts_data.telegram_id,
                    telegram_username=telegram_contacts_data.telegram_username,
                ),
            )

        raise StaffMemberAlreadyExistsError()

    def _validate(self, full_name: str) -> None:
        if len(full_name) < self._MIN_FULLNAME_LENGTH:
            raise InvalidFullNameError()
        if len(full_name) > self._MAX_FULLNAME_LENGTH:
            raise FullNameTooLongError()

    async def _get_user_role(self) -> list[StaffRole]:
        if user_role := await self._role_repository.load_with_names(
            [Role.USER]
        ):
            return list(user_role)
        return [
            StaffRole(
                entity_id=StaffRoleID(cast(int, None)), role_name=Role.USER
            )
        ]
