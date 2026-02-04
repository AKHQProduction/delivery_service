"""Add shop address fields, client address coordinates, and districts.

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

    op.add_column(
        "client_addresses", sa.Column("latitude", sa.Double(), nullable=True)
    )
    op.add_column(
        "client_addresses", sa.Column("longitude", sa.Double(), nullable=True)
    )
    op.create_check_constraint(
        "ck_client_addresses_coords_both_or_none",
        "client_addresses",
        "(latitude IS NULL) = (longitude IS NULL)",
    )

    op.create_table(
        "districts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
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
        sa.UniqueConstraint(
            "shop_id", "name", name="uq_district_name_per_shop"
        ),
    )

    op.add_column(
        "client_addresses",
        sa.Column(
            "district_id",
            sa.UUID(),
            sa.ForeignKey("districts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_client_addresses_district_id",
        "client_addresses",
        ["district_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_client_addresses_district_id", table_name="client_addresses"
    )
    op.drop_column("client_addresses", "district_id")
    op.drop_table("districts")

    op.drop_constraint(
        "ck_client_addresses_coords_both_or_none",
        "client_addresses",
        type_="check",
    )
    op.drop_column("client_addresses", "longitude")
    op.drop_column("client_addresses", "latitude")

    op.drop_constraint("ck_shops_coords_both_or_none", "shops", type_="check")
    op.drop_column("shops", "longitude")
    op.drop_column("shops", "latitude")
    op.drop_column("shops", "house")
    op.drop_column("shops", "street")
    op.drop_column("shops", "city")
