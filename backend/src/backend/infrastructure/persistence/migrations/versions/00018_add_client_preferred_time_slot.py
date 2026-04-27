"""Add client preferred time slot.

Revision ID: 00018
Revises: 00017
Create Date: 2026-04-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00018"
down_revision: str | Sequence[str] | None = "00017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CONSTRAINT_NAME = "fk_clients_preferred_time_slot_id_shop_delivery_time_slots"


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("preferred_time_slot_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        CONSTRAINT_NAME,
        "clients",
        "shop_delivery_time_slots",
        ["preferred_time_slot_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(CONSTRAINT_NAME, "clients", type_="foreignkey")
    op.drop_column("clients", "preferred_time_slot_id")
