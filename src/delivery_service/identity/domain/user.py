from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shared.domain.tracker import Tracker
from delivery_service.shared.domain.vo.tg_contacts import TelegramContacts


class User(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        tracker: Tracker,
        *,
        full_name: str,
        telegram_contacts: TelegramContacts | None = None,
        is_superuser: bool = False,
        is_active: bool = True,
    ) -> None:
        super().__init__(entity_id=entity_id, tracker=tracker)

        self._full_name = full_name
        self._telegram_contacts = telegram_contacts
        self._is_superuser = is_superuser
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
    def is_active(self) -> bool:
        return self._is_active
