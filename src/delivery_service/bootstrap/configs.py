from dataclasses import dataclass
from os import environ


@dataclass(frozen=True)
class TGConfig:
    admin_bot_token: str
    shop_bot_token: str
    use_redis_storage: bool


@dataclass(frozen=True)
class WebhookConfig:
    webhook_url: str
    webhook_admin_path: str
    webhook_shop_path: str
    webhook_host: str
    webhook_port: int


def load_bot_config() -> TGConfig:
    admin_bot_token = environ.get("ADMIN_BOT_TOKEN")
    shop_bot_token = environ.get("SHOP_BOT_TOKEN")
    use_redis_storage = environ.get("USE_REDIS_STORAGE", False)

    if admin_bot_token is None or shop_bot_token is None:
        raise ValueError(
            "Required bot tokens environment variables are missing"
        )

    return TGConfig(
        admin_bot_token=admin_bot_token,
        shop_bot_token=shop_bot_token,
        use_redis_storage=bool(use_redis_storage),
    )


def load_webhook_config() -> WebhookConfig:
    webhook_url = environ.get("WEBHOOK_URL")
    webhook_admin_path = environ.get("WEBHOOK_ADMIN_PATH")
    webhook_shop_path = environ.get("WEBHOOK_SHOP_PATH")
    webhook_host = environ.get("WEBHOOK_HOST")
    webhook_port = environ.get("WEBHOOK_PORT")

    if (
        webhook_url is None
        or webhook_admin_path is None
        or webhook_shop_path is None
        or webhook_host is None
        or webhook_port is None
    ):
        raise ValueError("Required webhook environment variables are missing")

    return WebhookConfig(
        webhook_url,
        webhook_admin_path,
        webhook_shop_path,
        webhook_host,
        int(webhook_port),
    )
