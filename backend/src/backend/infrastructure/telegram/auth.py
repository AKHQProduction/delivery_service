import hashlib
import hmac
import json
import logging
from collections.abc import Mapping
from typing import Any, NewType
from urllib.parse import parse_qsl, unquote

from fastapi import HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel

from backend.bootstrap.config import AppConfig, TelegramConfig

logger = logging.getLogger(__name__)

AUTH_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


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
    query_id: str
    user: WebAppUser
    auth_date: str
    hash: str


Headers = NewType("Headers", Mapping[str, str])


class WebAppAuth:
    def __init__(
        self,
        app_config: AppConfig,
        telegram_config: TelegramConfig,
        headers: Headers,
    ) -> None:
        self._headers = headers
        self._app_config = app_config
        self._telegram_config = telegram_config

    def with_init_data(self) -> InitData:
        logger.debug("Initialize auth with headers: %s", self._headers)
        if self._app_config.debug:
            return self._validate_fake_headers_param(self._get_headers_param())
        return self._validate_headers_param(self._get_headers_param())

    def _get_headers_param(self) -> str:
        authorization = self._headers.get("Authorization")
        schema, param = get_authorization_scheme_param(authorization)

        if not authorization or schema.lower() != "bearer":
            raise AUTH_ERROR
        return param

    def _validate_headers_param(self, param: str) -> InitData:
        parsed_init_data = self._parse_init_data(param)

        received_hash: str | None = parsed_init_data.get("hash")
        if not received_hash:
            raise AUTH_ERROR

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

        if received_hash != computed_hash:
            raise AUTH_ERROR

        if "user" in parsed_init_data:
            if isinstance(parsed_init_data["user"], str):
                parsed_init_data["user"] = json.loads(parsed_init_data["user"])
            if isinstance(parsed_init_data["user"], dict):
                parsed_init_data["user"] = WebAppUser(
                    **parsed_init_data["user"]
                )

        parsed_init_data["hash"] = received_hash
        return InitData(**parsed_init_data)

    def _validate_fake_headers_param(self, param: str) -> InitData:
        return self._get_dummy_init_data(int(param))

    @staticmethod
    def _parse_init_data(param: str) -> dict[str, Any]:
        return dict(parse_qsl(param))

    @staticmethod
    def _get_dummy_init_data(user_id: int) -> InitData:
        return InitData(
            query_id="",
            user=WebAppUser(
                id=user_id,
                first_name="",
                last_name="",
                username="",
                language_code="",
                is_premium=True,
                added_to_attachment_menu=True,
                allows_write_to_pm=True,
                photo_url="",
            ),
            auth_date="",
            hash="",
        )
