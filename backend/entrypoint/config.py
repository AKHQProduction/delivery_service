import logging
from dataclasses import dataclass

from environs import Env

from infrastructure.tg.config import WebhookConfig

logger = logging.getLogger(__name__)


@dataclass
class TgBot:
    admin_bot_token: str
    shop_bot_token: str
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        admin_bot_token = env.str("ADMIN_BOT_TOKEN")
        shop_bot_token = env.str("SHOP_BOT_TOKEN")
        use_redis = env.bool("USE_REDIS")

        return TgBot(
            admin_bot_token=admin_bot_token,
            shop_bot_token=shop_bot_token,
            use_redis=use_redis,
        )


@dataclass
class RedisConfig:
    redis_host: str
    redis_port: int

    def dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(redis_port=redis_port, redis_host=redis_host)


@dataclass
class Config:
    tg_bot: TgBot
    webhook: WebhookConfig
    redis: RedisConfig | None = None


def load_config() -> Config:
    env = Env()
    env.read_env(".env")

    config = Config(
        tg_bot=TgBot.from_env(env),
        webhook=WebhookConfig.from_env(env),
        redis=RedisConfig.from_env(env),
    )

    logger.info("Config successfully loaded")

    return config
