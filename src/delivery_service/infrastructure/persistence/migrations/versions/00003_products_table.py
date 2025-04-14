"""Products table

Revision ID: 00003
Revises: 00002
Create Date: 2025-04-09 22:02:01.122058

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "00003"
down_revision: Union[str, None] = "00002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "product_type",
            sa.Enum("WATER", "ACCESSORIES", name="producttype"),
            nullable=False,
        ),
        sa.Column("metadata_path", sa.String(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
            name=op.f("fk_product_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product")),
        sa.UniqueConstraint("id", name=op.f("uq_product_id")),
    )
    op.create_unique_constraint(op.f("uq_products_id"), "products", ["id"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_products_id"), "products", type_="unique")
    op.drop_table("products")

    op.execute("DROP TYPE IF EXISTS producttype")
