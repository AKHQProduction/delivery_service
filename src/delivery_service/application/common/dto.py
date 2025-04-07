from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None
