from dataclasses import dataclass

from environs import Env


@dataclass
class ProjectConfig:
    admin_id: int


@dataclass
class WebhookConfig:
    webhook_url: str
    webhook_admin_path: str
    webhook_shop_path: str
    webhook_host: str
    webhook_port: int

    @staticmethod
    def from_env(env: Env):
        webhook_url = env.str("WEBHOOK_URL")
        webhook_admin_path = env.str("WEBHOOK_ADMIN_PATH")
        webhook_shop_path = env.str("WEBHOOK_SHOP_PATH")
        webhook_host = env.str("WEBHOOK_HOST")
        webhook_port = env.int("WEBHOOK_PORT")

        return WebhookConfig(
            webhook_url=webhook_url,
            webhook_admin_path=webhook_admin_path,
            webhook_shop_path=webhook_shop_path,
            webhook_host=webhook_host,
            webhook_port=webhook_port,
        )
