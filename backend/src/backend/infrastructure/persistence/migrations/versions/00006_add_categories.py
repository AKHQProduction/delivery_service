"""Add categories table and update products.

Revision ID: 00006
Revises: 00005
Create Date: 2025-12-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00006"
down_revision: str | Sequence[str] | None = "00005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
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
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "shop_id", "name", name="uq_category_name_per_shop"
        ),
    )

    op.add_column(
        "products",
        sa.Column("category_id", sa.UUID(), nullable=True),
    )

    op.create_foreign_key(
        "fk_products_category_id",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_column("products", "category")


def downgrade() -> None:
    op.add_column(
        "products",
        sa.Column("category", sa.String(), nullable=True),
    )

    op.execute("UPDATE products SET category = 'OTHER' WHERE category IS NULL")

    op.alter_column("products", "category", nullable=False)

    op.drop_constraint(
        "fk_products_category_id", "products", type_="foreignkey"
    )

    op.drop_column("products", "category_id")

    op.drop_table("categories")
