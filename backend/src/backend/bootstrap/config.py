from os import environ as env
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    debug: bool = Field(alias="DEBUG", default=True)


class TelegramConfig(BaseModel):
    admin_token: str = Field(alias="ADMIN_BOT_TOKEN")
    use_redis: bool = Field(alias="USE_REDIS", default=False)


class Config(BaseModel):
    def __init__(self) -> None:
        load_dotenv(
            dotenv_path=Path(__file__).parents[4] / ".env", override=False
        )

        super().__init__()

    app_config: AppConfig = Field(
        default_factory=lambda: AppConfig.model_validate(env)
    )

    telegram_config: TelegramConfig = Field(
        default_factory=lambda: TelegramConfig.model_validate(env)
    )
