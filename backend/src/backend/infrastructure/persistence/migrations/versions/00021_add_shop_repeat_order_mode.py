"""Add shop repeat order mode.

Revision ID: 00021
Revises: 00020
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00021"
down_revision: str | Sequence[str] | None = "00020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "shops",
        sa.Column(
            "repeat_order_mode",
            sa.String(length=32),
            server_default="CONFIRMATION_REQUIRED",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("shops", "repeat_order_mode")
