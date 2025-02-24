from enum import StrEnum
from typing import NewType
from uuid import UUID

from delivery_service.core.shared.entity import Entity
from delivery_service.core.shared.tg_contacts import TelegramContacts

UserID = NewType("UserID", UUID)


class UserRole(StrEnum):
    SUPERUSER = "superuser"
    SHOP_OWNER = "shop_owner"
    SHOP_MANAGER = "shop_manager"
    COURIER = "courier"
    USER = "user"


class User(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        *,
        full_name: str,
        telegram_contacts: TelegramContacts | None = None,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._full_name = full_name
        self._telegram_contacts = telegram_contacts
        self._role = role
        self._is_active = is_active

    def edit_telegram_contacts(
        self, telegram_id: int, telegram_username: str | None = None
    ) -> None:
        self._telegram_contacts = TelegramContacts(
            telegram_id=telegram_id, telegram_username=telegram_username
        )

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def telegram_contacts(self) -> TelegramContacts | None:
        return self._telegram_contacts

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active
