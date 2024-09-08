from dataclasses import dataclass
import logging

from environs import Env

from infrastructure.tg.config import WebhookConfig

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
class Config:
    tg_bot: TgBot
    webhook: WebhookConfig


def load_config() -> Config:
    env = Env()
    env.read_env(".env")

    config = Config(
            tg_bot=TgBot.from_env(env),
            webhook=WebhookConfig.from_env(env)
    )

    logger.info("Config successfully loaded")

    return config
