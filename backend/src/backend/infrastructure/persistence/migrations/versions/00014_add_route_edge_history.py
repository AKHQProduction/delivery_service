"""Add route_edge_history table.

Revision ID: 00014
Revises: 00013
Create Date: 2026-02-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "00014"
down_revision: str | Sequence[str] | None = "00013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_edge_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("from_coords", ARRAY(sa.Double()), nullable=False),
        sa.Column("to_coords", ARRAY(sa.Double()), nullable=False),
        sa.Column(
            "times_seen",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "last_seen",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "shop_id",
            "from_coords",
            "to_coords",
            name="uq_route_edge_shop_coords",
        ),
    )

    op.create_index(
        "ix_route_edge_shop_last_seen",
        "route_edge_history",
        ["shop_id", "last_seen"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_route_edge_shop_last_seen", table_name="route_edge_history"
    )
    op.drop_table("route_edge_history")
