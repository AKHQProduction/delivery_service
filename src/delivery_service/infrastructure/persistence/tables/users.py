import sqlalchemy as sa
from sqlalchemy import and_, join
from sqlalchemy.orm import composite

from delivery_service.domain.shared.vo.tg_contacts import TelegramContacts
from delivery_service.domain.users.user import User
from delivery_service.infrastructure.persistence.tables.base import (
    MAPPER_REGISTRY,
)

USERS_TABLE = sa.Table(
    "users",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True, unique=True),
    sa.Column("full_name", sa.String, nullable=False),
    sa.Column("is_superuser", sa.Boolean, default=False, nullable=False),
    sa.Column("is_active", sa.Boolean, default=True, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        nullable=False,
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
        nullable=True,
    ),
)

SOCIAL_NETWORKS_TABLE = sa.Table(
    "social_networks",
    MAPPER_REGISTRY.metadata,
    sa.Column(
        "user_id",
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column("telegram_id", sa.BIGINT, nullable=False),
    sa.Column("telegram_username", sa.String, nullable=True),
)

MAPPER_REGISTRY.map_imperatively(
    User,
    join(
        USERS_TABLE,
        SOCIAL_NETWORKS_TABLE,
        and_(USERS_TABLE.c.id == SOCIAL_NETWORKS_TABLE.c.user_id),
    ),
    properties={
        "_entity_id": USERS_TABLE.c.id,
        "_full_name": USERS_TABLE.c.full_name,
        "_telegram_contacts": composite(
            TelegramContacts,
            SOCIAL_NETWORKS_TABLE.c.telegram_id,
            SOCIAL_NETWORKS_TABLE.c.telegram_username,
        ),
        "is_superuser": USERS_TABLE.c.is_superuser,
        "is_active": USERS_TABLE.c.is_active,
    },
)
