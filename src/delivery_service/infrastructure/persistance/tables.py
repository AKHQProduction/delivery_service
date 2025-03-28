import sqlalchemy as sa

from delivery_service.infrastructure.persistance.registry import (
    MAPPER_REGISTRY,
)

USERS_TABLE = sa.Table("users", MAPPER_REGISTRY.metadata)
