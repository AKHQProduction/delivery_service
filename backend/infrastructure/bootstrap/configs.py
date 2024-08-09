from dataclasses import dataclass
import logging
import os

from infrastructure.persistence.config import DBConfig
from dotenv import load_dotenv


@dataclass
class AllConfigs:
    db: DBConfig


def load_all_configs() -> AllConfigs:
    load_dotenv()

    db_config = DBConfig(
        host=os.getenv("DB_HOST"),
        db_name=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    logging.info("Config loaded.")

    return AllConfigs(db=db_config)
