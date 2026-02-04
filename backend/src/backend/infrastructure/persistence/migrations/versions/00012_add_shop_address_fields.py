"""Add shop address fields (city, street, house, latitude, longitude).

Revision ID: 00012
Revises: 00011
Create Date: 2026-02-04

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00012"
down_revision: str | Sequence[str] | None = "00011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("shops", sa.Column("city", sa.String(), nullable=True))
    op.add_column("shops", sa.Column("street", sa.String(), nullable=True))
    op.add_column("shops", sa.Column("house", sa.String(), nullable=True))
    op.add_column("shops", sa.Column("latitude", sa.Double(), nullable=True))
    op.add_column("shops", sa.Column("longitude", sa.Double(), nullable=True))
    op.create_check_constraint(
        "ck_shops_coords_both_or_none",
        "shops",
        "(latitude IS NULL) = (longitude IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_shops_coords_both_or_none", "shops", type_="check")
    op.drop_column("shops", "longitude")
    op.drop_column("shops", "latitude")
    op.drop_column("shops", "house")
    op.drop_column("shops", "street")
    op.drop_column("shops", "city")
