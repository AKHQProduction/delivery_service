"""Replace address_type with comment in addresses table.

Revision ID: 00009
Revises: 00008
Create Date: 2026-01-15

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00009"
down_revision: str | Sequence[str] | None = "00008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("client_addresses", "address_type")
    op.add_column(
        "client_addresses",
        sa.Column("comment", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("client_addresses", "comment")
    op.add_column(
        "client_addresses",
        sa.Column(
            "address_type",
            sa.String(),
            nullable=False,
            server_default="APARTMENT",
        ),
    )
