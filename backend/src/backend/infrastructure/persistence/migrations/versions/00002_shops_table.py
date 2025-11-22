"""Shops table.

Revision ID: 00002
Revises: 00001
Create Date: 2025-11-09 03:37:49.637167

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00002"
down_revision: str | Sequence[str] | None = "00001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Insert default roles
    op.execute(
        """
                INSERT INTO roles (name) VALUES
                ('OWNER'),
                ('MANAGER'),
                ('COURIER')
            """
    )

    op.create_table(
        "shops",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shop_memberships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_shop_membership_user"),
    )


def downgrade() -> None:
    op.drop_table("shop_memberships")
    op.drop_table("shops")
    op.drop_table("roles")
