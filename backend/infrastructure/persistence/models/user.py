from sqlalchemy import (
    Column,
    Table,
    BigInteger,
    String,
    Enum,
    Boolean
)

from entities.user.model import RoleName, User
from infrastructure.persistence.models.base import (
    created_at_column,
    mapper_registry,
    updated_at_column
)

users_table = Table(
        "users",
        mapper_registry.metadata,
        Column(
                "user_id",
                BigInteger,
                primary_key=True,
                unique=True,
        ),
        Column(
                "full_name",
                String(128),
                nullable=False
        ),
        Column(
                "username",
                String(255),
                nullable=True,
                default=None,
        ),
        Column(
                "phone_number",
                String(12),
                nullable=True,
                default=None
        ),
        Column(
                "role",
                Enum(RoleName),
                default=RoleName.USER,
                nullable=False
        ),
        Column(
                "is_active",
                Boolean,
                default=True,
                nullable=False
        ),
        created_at_column,
        updated_at_column
)


def map_users_table():
    mapper_registry.map_imperatively(User, users_table)
