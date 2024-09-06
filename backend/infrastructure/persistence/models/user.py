import sqlalchemy as sa
from sqlalchemy.orm import relationship

from entities.user.models import User
from infrastructure.persistence.models import mapper_registry
from infrastructure.persistence.models.associations import (
    association_between_shops_and_users
)

users_table = sa.Table(
        "users",
        mapper_registry.metadata,
        sa.Column(
                "user_id",
                sa.BigInteger,
                primary_key=True,
                unique=True,
        ),
        sa.Column(
                "full_name",
                sa.String(128),
                nullable=False
        ),
        sa.Column(
                "username",
                sa.String(255),
                nullable=True,
                default=None,
        ),
        sa.Column(
                "is_active",
                sa.Boolean,
                default=True,
                nullable=False
        ),
        sa.Column(
                "created_at",
                sa.DateTime,
                default=sa.func.now(),
                server_default=sa.func.now()
        ),
        sa.Column(
                "updated_at",
                sa.DateTime,
                default=sa.func.now(),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
                server_onupdate=sa.func.now(),
        )
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
            User,
            users_table,
            properties={
                "shops": relationship(
                        "Shop",
                        secondary=association_between_shops_and_users,
                        back_populates="users",
                )
            }
    )
