from dataclasses import dataclass
import logging

from environs import Env

logger = logging.getLogger(__name__)


@dataclass
class TgBot:
    admin_bot_token: str
    shop_bot_token: str

    @staticmethod
    def from_env(env: Env):
        admin_bot_token = env.str("ADMIN_BOT_TOKEN")
        shop_bot_token = env.str("SHOP_BOT_TOKEN")

        return TgBot(
                admin_bot_token=admin_bot_token,
                shop_bot_token=shop_bot_token
        )


@dataclass
class TgWebhook:
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

        return TgWebhook(
                webhook_url=webhook_url,
                webhook_admin_path=webhook_admin_path,
                webhook_shop_path=webhook_shop_path,
                webhook_host=webhook_host,
                webhook_port=webhook_port
        )


@dataclass
class Config:
    tg_bot: TgBot
    webhook: TgWebhook


def load_config() -> Config:
    env = Env()
    env.read_env(".env")

    config = Config(
            tg_bot=TgBot.from_env(env),
            webhook=TgWebhook.from_env(env)
    )

    logger.info("Config successfully loaded")

    return config
