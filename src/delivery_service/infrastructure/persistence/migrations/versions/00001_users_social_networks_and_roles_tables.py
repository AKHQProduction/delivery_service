"""Users, social networks and roles tables

Revision ID: 00001
Revises:
Create Date: 2025-03-31 14:07:04.723762

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "00001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "name",
            sa.Enum("SHOP_OWNER", "SHOP_MANAGER", "COURIER", name="role"),
            nullable=False,
            unique=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("id", name=op.f("uq_users_id")),
    )

    op.create_table(
        "social_networks",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("telegram_id", sa.BIGINT(), nullable=False),
        sa.Column("telegram_username", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_social_networks_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_social_networks")),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name=op.f("fk_user_roles_role_id_roles"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_roles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "role_id", name=op.f("pk_user_roles")
        ),
    )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("social_networks")
    op.drop_table("users")
    op.drop_table("roles")

    op.execute("DROP TYPE IF EXISTS role")
