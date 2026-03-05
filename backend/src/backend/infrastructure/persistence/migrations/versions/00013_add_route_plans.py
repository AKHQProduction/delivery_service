"""Add route_plans table.

Revision ID: 00013
Revises: 00012
Create Date: 2026-02-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "00013"
down_revision: str | Sequence[str] | None = "00012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "route_plans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("time_slot_id", sa.UUID(), nullable=True),
        sa.Column("order_sequence", ARRAY(sa.UUID()), nullable=False),
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
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["time_slot_id"],
            ["shop_delivery_time_slots.id"],
            ondelete="SET NULL",
        ),
    )

    op.create_index(
        "ix_route_plans_shop_date_slot",
        "route_plans",
        ["shop_id", "delivery_date", "time_slot_id"],
        unique=True,
        postgresql_where=sa.text("time_slot_id IS NOT NULL"),
    )
    op.create_index(
        "ix_route_plans_shop_date_no_slot",
        "route_plans",
        ["shop_id", "delivery_date"],
        unique=True,
        postgresql_where=sa.text("time_slot_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_route_plans_shop_date_no_slot", table_name="route_plans")
    op.drop_index("ix_route_plans_shop_date_slot", table_name="route_plans")
    op.drop_table("route_plans")
