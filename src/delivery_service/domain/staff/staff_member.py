from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.tg_contacts import (
    TelegramContacts,
)
from delivery_service.domain.staff.staff_role import RoleCollection, StaffRole


class StaffMember(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        *,
        full_name: str,
        telegram_contacts: TelegramContacts,
        roles: RoleCollection,
        is_superuser: bool = False,
        is_active: bool = True,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._full_name = full_name
        self._telegram_contacts = telegram_contacts
        self._roles = roles
        self._is_superuser = is_superuser
        self._is_active = is_active

    def add_role(self, role: StaffRole) -> None:
        self._roles.add(role)

    def edit_telegram_contacts(
        self, telegram_id: int, telegram_username: str | None = None
    ) -> None:
        self._telegram_contacts.edit_contacts(
            telegram_id=telegram_id, telegram_username=telegram_username
        )

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def role(self) -> RoleCollection:
        return self._roles

    @property
    def telegram_contacts(self) -> TelegramContacts | None:
        return self._telegram_contacts

    @property
    def is_active(self) -> bool:
        return self._is_active
