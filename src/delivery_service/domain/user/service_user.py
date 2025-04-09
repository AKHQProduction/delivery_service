from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.new_types import Empty
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.tg_contacts import TelegramContacts


class ServiceUser(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        *,
        full_name: str,
        telegram_contacts: TelegramContacts,
        is_superuser: bool = False,
        is_active: bool = True,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._full_name = full_name
        self._telegram_contacts = telegram_contacts
        self._is_superuser = is_superuser
        self._is_active = is_active

    def edit_telegram_contacts(
        self, telegram_id: int | None, telegram_username: str | None | Empty
    ) -> None:
        self._telegram_contacts = self._telegram_contacts.edit_contacts(
            telegram_id, telegram_username
        )

    def edit_full_name(self, full_name: str) -> None:
        self._full_name = full_name

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def telegram_contacts(self) -> TelegramContacts:
        return self._telegram_contacts

    @property
    def is_active(self) -> bool:
        return self._is_active
