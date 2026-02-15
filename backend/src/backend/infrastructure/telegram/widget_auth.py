import hashlib
import hmac
import time

from pydantic import BaseModel

from backend.application.errors import AuthorizationError
from backend.bootstrap.config import TelegramConfig

FRESHNESS_WINDOW = 300


class WidgetAuthError(AuthorizationError):
    pass


class TelegramWidgetData(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class WidgetAuth:
    def __init__(self, telegram_config: TelegramConfig) -> None:
        self._telegram_config = telegram_config

    def validate(self, data: TelegramWidgetData) -> int:
        self._check_freshness(data.auth_date)
        self._check_hash(data)
        return data.id

    def _check_freshness(self, auth_date: int) -> None:
        if time.time() - auth_date > FRESHNESS_WINDOW:
            raise WidgetAuthError

    def _check_hash(self, data: TelegramWidgetData) -> None:
        secret_key = hashlib.sha256(
            self._telegram_config.admin_token.encode()
        ).digest()

        fields = sorted(
            (k, v)
            for k, v in data.model_dump(
                exclude={"hash"}, exclude_none=True
            ).items()
        )
        data_check_string = "\n".join(f"{k}={v}" for k, v in fields)

        computed_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(data.hash, computed_hash):
            raise WidgetAuthError
