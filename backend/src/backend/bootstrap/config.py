from os import environ as env
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    debug: bool = Field(alias="DEBUG", default=True)


class TelegramConfig(BaseModel):
    admin_token: str = Field(alias="ADMIN_BOT_TOKEN")
    use_redis: bool = Field(alias="USE_REDIS", default=True)


class RedisConfig(BaseModel):
    host: str = Field(alias="REDIS_HOST")
    port: int = Field(alias="REDIS_PORT")
    password: str = Field(alias="REDIS_PASSWORD")

    @property
    def default_uri(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/"

    @property
    def fsm_uri(self) -> str:
        return self.default_uri + "0"

    @property
    def persistence_uri(self) -> str:
        return self.default_uri + "1"


class PostgresConfig(BaseModel):
    host: str = Field(alias="DB_HOST")
    db_name: str = Field(alias="POSTGRES_DB")
    user: str = Field(alias="POSTGRES_USER")
    port: int = Field(alias="POSTGRES_PORT")
    password: str = Field(alias="POSTGRES_PASSWORD")

    @property
    def uri(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password}@{self.host}"
            f":{self.port}/{self.db_name}"
        )


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

    redis_config: RedisConfig = Field(
        default_factory=lambda: RedisConfig.model_validate(env)
    )

    postgres_config: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig.model_validate(env)
    )
