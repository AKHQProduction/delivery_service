import hashlib
import hmac
from urllib.parse import parse_qsl, unquote, urlencode

import pytest

from backend.bootstrap.config import AppConfig, Config, TelegramConfig
from backend.infrastructure.telegram.auth import (
    AUTH_ERROR,
    Headers,
    WebAppAuth,
)


@pytest.fixture()
def telegram_token() -> str:
    return "test_bot_token_12345"


@pytest.fixture()
def config(telegram_token: str) -> Config:
    config = Config()
    config.telegram_config = TelegramConfig(
        ADMIN_BOT_TOKEN=telegram_token, USE_REDIS=False
    )
    config.app_config = AppConfig(DEBUG=False)
    return config


@pytest.fixture()
def debug_config(telegram_token: str) -> Config:
    config = Config()
    config.telegram_config = TelegramConfig(
        ADMIN_BOT_TOKEN=telegram_token, USE_REDIS=False
    )
    config.app_config = AppConfig(DEBUG=True)
    return config


def generate_init_data_with_hash(data: dict[str, str], bot_token: str) -> str:
    encoded_data = urlencode(data)
    parsed = dict(parse_qsl(encoded_data))

    sorted_data = sorted([(k, unquote(str(v))) for k, v in parsed.items()])
    data_check_string = "\n".join(f"{k}-{v}" for k, v in sorted_data)

    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256,
    ).digest()

    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    return encoded_data + f"&hash={hash_value}"


def test_valid_init_data_with_correct_hash(
    config: Config, telegram_token: str
):
    user_json = (
        '{"id": 123, "first_name": "John", "last_name": "Doe", '
        '"username": "johndoe", "language_code": "en", "is_premium": true, '
        '"added_to_attachment_menu": false, "allows_write_to_pm": true, '
        '"photo_url": "https://example.com/photo.jpg"}'
    )
    data = {
        "query_id": "test_query_id",
        "user": user_json,
        "auth_date": "1234567890",
    }

    init_data = generate_init_data_with_hash(data, telegram_token)
    headers = Headers({"Authorization": f"Bearer {init_data}"})

    auth = WebAppAuth(config, headers)
    result = auth.with_init_data()

    assert result.query_id == "test_query_id"
    assert result.user.id == 123
    assert result.user.first_name == "John"
    assert result.user.last_name == "Doe"
    assert result.auth_date == "1234567890"


def test_invalid_hash_raises_auth_error(config: Config):
    user_json = (
        '{"id": 123, "first_name": "John", "last_name": "Doe", '
        '"username": "johndoe", "language_code": "en", "is_premium": true, '
        '"added_to_attachment_menu": false, "allows_write_to_pm": true, '
        '"photo_url": "https://example.com/photo.jpg"}'
    )
    data = {
        "query_id": "test_query_id",
        "user": user_json,
        "auth_date": "1234567890",
        "hash": "invalid_hash_value",
    }

    init_data = urlencode(data)
    headers = Headers({"Authorization": f"Bearer {init_data}"})

    auth = WebAppAuth(config, headers)

    with pytest.raises(type(AUTH_ERROR)):
        auth.with_init_data()


def test_missing_hash_raises_auth_error(config: Config):
    data = {
        "query_id": "test_query_id",
        "auth_date": "1234567890",
    }

    init_data = urlencode(data)
    headers = Headers({"Authorization": f"Bearer {init_data}"})

    auth = WebAppAuth(config, headers)

    with pytest.raises(type(AUTH_ERROR)):
        auth.with_init_data()


def test_missing_authorization_header_raises_auth_error(config: Config):
    headers = Headers({})

    auth = WebAppAuth(config, headers)

    with pytest.raises(type(AUTH_ERROR)):
        auth.with_init_data()


def test_invalid_authorization_scheme_raises_auth_error(config: Config):
    headers = Headers({"Authorization": "Basic some_token"})

    auth = WebAppAuth(config, headers)

    with pytest.raises(type(AUTH_ERROR)):
        auth.with_init_data()


def test_debug_mode_returns_dummy_data(debug_config: Config):
    user_id = 999
    headers = Headers({"Authorization": f"Bearer {user_id}"})

    auth = WebAppAuth(debug_config, headers)
    result = auth.with_init_data()

    assert result.user.id == user_id
    assert result.query_id == ""
    assert result.auth_date == ""
    assert result.hash == ""


def test_url_encoded_values_are_decoded(config: Config, telegram_token: str):
    user_json = (
        '{"id": 123, "first_name": "John", "last_name": "Doe", '
        '"username": "johndoe", "language_code": "en", "is_premium": true, '
        '"added_to_attachment_menu": false, "allows_write_to_pm": true, '
        '"photo_url": "https://example.com/photo.jpg"}'
    )
    data = {
        "query_id": "test query",
        "user": user_json,
        "auth_date": "1234567890",
    }

    init_data = generate_init_data_with_hash(data, telegram_token)
    headers = Headers({"Authorization": f"Bearer {init_data}"})

    auth = WebAppAuth(config, headers)
    result = auth.with_init_data()

    assert result.query_id == "test query"
