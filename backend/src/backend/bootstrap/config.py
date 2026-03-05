import json
from os import environ as env
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


class AppConfig(BaseModel):
    debug: bool = Field(alias="DEBUG", default=True)
    debug_user_id: int = Field(alias="DEBUG_USER_ID", default=1)
    cors_origins: list[str] = Field(alias="CORS_ORIGINS", default=["*"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


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
    pool_size: int = Field(alias="DB_POOL_SIZE", default=10)
    max_overflow: int = Field(alias="DB_MAX_OVERFLOW", default=5)

    @property
    def uri(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password}@{self.host}"
            f":{self.port}/{self.db_name}"
        )


class WebhookConfig(BaseModel):
    webhook_url: str = Field(alias="WEBHOOK_URL")
    webhook_path: str = Field(alias="WEBHOOK_PATH")
    webhook_host: str = Field(alias="WEBHOOK_HOST")
    webhook_port: int = Field(alias="WEBHOOK_PORT")


class OTelConfig(BaseModel):
    enabled: bool = Field(alias="OTEL_ENABLED", default=True)
    service_name: str = Field(
        alias="OTEL_SERVICE_NAME", default="water-delivery"
    )
    exporter_endpoint: str = Field(
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
        default="http://otel-collector:4317",
    )


class OSRMConfig(BaseModel):
    url: str = Field(
        alias="OSRM_URL", default="https://router.project-osrm.org"
    )


class NominatimConfig(BaseModel):
    url: str = Field(
        alias="NOMINATIM_URL",
        default="https://nominatim.openstreetmap.org",
    )


class GoogleGeocoderConfig(BaseModel):
    api_key: str = Field(alias="GOOGLE_GEOCODER_API_KEY", default="")


class HereGeocoderConfig(BaseModel):
    api_key: str = Field(alias="HERE_GEOCODER_API_KEY", default="")


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

    webhook_config: WebhookConfig = Field(
        default_factory=lambda: WebhookConfig.model_validate(env)
    )

    otel_config: OTelConfig = Field(
        default_factory=lambda: OTelConfig.model_validate(env)
    )

    osrm_config: OSRMConfig = Field(
        default_factory=lambda: OSRMConfig.model_validate(env)
    )

    nominatim_config: NominatimConfig = Field(
        default_factory=lambda: NominatimConfig.model_validate(env)
    )

    google_geocoder_config: GoogleGeocoderConfig = Field(
        default_factory=lambda: GoogleGeocoderConfig.model_validate(env)
    )

    here_geocoder_config: HereGeocoderConfig = Field(
        default_factory=lambda: HereGeocoderConfig.model_validate(env)
    )
