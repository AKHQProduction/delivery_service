from dataclasses import dataclass
import os

from environs import Env


@dataclass
class BaseDBConfig:
    host: str
    db_name: str
    user: str
    password: str

    def get_connection_url(self) -> str:
        return (
                f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}"
                f"/{self.db_name}"
        )


@dataclass
class DBConfig(BaseDBConfig):
    pass


@dataclass
class AlembicDBConfig(BaseDBConfig):
    pass


def load_alembic_config() -> AlembicDBConfig:
    env = Env()
    env.read_env(".env")

    config = AlembicDBConfig(
            host=env.str("DB_HOST"),
            db_name=env.str("POSTGRES_DB"),
            user=env.str("POSTGRES_USER"),
            password=env.str("POSTGRES_PASSWORD"),
    )

    return config
