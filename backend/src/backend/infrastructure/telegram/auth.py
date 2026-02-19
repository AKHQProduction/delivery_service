import hashlib
import hmac
import json
import logging
from collections.abc import Mapping
from typing import Any, NewType
from urllib.parse import parse_qsl, unquote

from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel

from backend.application.errors import AuthorizationError
from backend.bootstrap.config import AppConfig, TelegramConfig

logger = logging.getLogger(__name__)

Headers = NewType("Headers", Mapping[str, str])


class WebAppAuthError(AuthorizationError):
    pass


class WebAppUser(BaseModel):
    id: int
    first_name: str
    last_name: str = ""
    username: str | None = None
    language_code: str = ""
    is_premium: bool = False
    added_to_attachment_menu: bool = False
    allows_write_to_pm: bool = False
    photo_url: str = ""


class InitData(BaseModel):
    query_id: str | None = None
    user: WebAppUser
    auth_date: str
    hash: str


class WebAppAuth:
    def __init__(
        self,
        app_config: AppConfig,
        telegram_config: TelegramConfig,
    ) -> None:
        self._app_config = app_config
        self._telegram_config = telegram_config

    def validate(self, headers: Headers) -> int:
        if self._app_config.debug:
            return self._validate_fake(headers)
        param = self._get_bearer_token(headers)
        init_data = self._parse_and_verify(param)
        return init_data.user.id

    def _get_bearer_token(self, headers: Headers) -> str:
        authorization = headers.get("Authorization")
        schema, param = get_authorization_scheme_param(authorization)

        if not authorization or schema.lower() != "bearer":
            raise WebAppAuthError
        return param

    def _parse_and_verify(self, param: str) -> InitData:
        parsed_init_data = self._parse_init_data(param)

        received_hash: str | None = parsed_init_data.get("hash")
        if not received_hash:
            raise WebAppAuthError

        fields: list[tuple[str, str]] = sorted([
            (key, unquote(str(value)))
            for key, value in parsed_init_data.items()
            if key != "hash"
        ])
        data_check_string = "\n".join(f"{k}={v}" for k, v in fields)

        secret_key = hmac.new(
            b"WebAppData",
            self._telegram_config.admin_token.encode(),
            hashlib.sha256,
        ).digest()

        computed_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_hash, computed_hash):
            raise WebAppAuthError

        if "user" in parsed_init_data:
            if isinstance(parsed_init_data["user"], str):
                parsed_init_data["user"] = json.loads(parsed_init_data["user"])
            if isinstance(parsed_init_data["user"], dict):
                parsed_init_data["user"] = WebAppUser(
                    **parsed_init_data["user"]
                )

        parsed_init_data["hash"] = received_hash
        return InitData(**parsed_init_data)

    def _validate_fake(self, headers: Headers) -> int:
        authorization = headers.get("Authorization")
        if authorization:
            _, param = get_authorization_scheme_param(authorization)
            if param and param.isdigit():
                return int(param)
        return self._app_config.debug_user_id

    @staticmethod
    def _parse_init_data(param: str) -> dict[str, Any]:
        return dict(parse_qsl(param))
