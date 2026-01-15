"""Payment method and paid flag for orders.

Revision ID: 00008
Revises: 00007
Create Date: 2026-01-14 21:48:09.250595

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00008"
down_revision: str | Sequence[str] | None = "00007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "is_paid", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "payment_method",
            sa.String(),
            nullable=False,
            server_default="OTHER",
        ),
    )


def downgrade() -> None:
    op.drop_column("orders", "payment_method")
    op.drop_column("orders", "is_paid")
