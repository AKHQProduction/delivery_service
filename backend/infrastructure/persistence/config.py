from dataclasses import dataclass
import os


@dataclass
class BaseDBConfig:
    host: str
    db_name: str
    user: str
    password: str

    def get_connection_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}/{self.db_name}"


@dataclass
class DBConfig(BaseDBConfig):
    pass


@dataclass
class AlembicDBConfig(BaseDBConfig):
    pass


def load_alembic_config() -> AlembicDBConfig:
    config = AlembicDBConfig(
        host=os.getenv("DB_HOST"),
        db_name=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    return config