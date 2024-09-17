import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from infrastructure.geopy.config import GeoConfig
from infrastructure.persistence.config import DBConfig
from infrastructure.s3.config import S3Config
from infrastructure.tg.config import WebhookConfig


@dataclass
class AllConfigs:
    db: DBConfig
    geo: GeoConfig
    webhook: WebhookConfig
    s3: S3Config


def load_all_configs() -> AllConfigs:
    load_dotenv()

    db_config = DBConfig(
        host=os.getenv("DB_HOST"),
        db_name=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    geo_config = GeoConfig(
        city=os.getenv("CITY"),
        user_agent=os.getenv("GEO_USER_AGENT"),
    )

    webhook_config = WebhookConfig(
        webhook_url=os.getenv("WEBHOOK_URL"),
        webhook_shop_path=os.getenv("WEBHOOK_SHOP_PATH"),
        webhook_admin_path=os.getenv("WEBHOOK_ADMIN_PATH"),
        webhook_host=os.getenv("WEBHOOK_HOST"),
        webhook_port=int(os.getenv("WEBHOOK_PORT")),
    )

    s3_config = S3Config(
        endpoint_url=os.getenv("MINIO_URL"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    )

    logging.info("Config loaded.")

    return AllConfigs(
        db=db_config, geo=geo_config, webhook=webhook_config, s3=s3_config
    )
