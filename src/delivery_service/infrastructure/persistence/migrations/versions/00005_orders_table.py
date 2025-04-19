"""Orders table

Revision ID: 00005
Revises: 00004
Create Date: 2025-04-19 17:51:14.814581

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "00005"
down_revision: Union[str, None] = "00004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=True),
        sa.Column(
            "delivery_preference",
            sa.Enum("MORNING", "AFTERNOON", name="deliverypreference"),
            nullable=False,
        ),
        sa.Column("delivery_date", sa.Date(), nullable=False),
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
            ["customer_id"],
            ["users.id"],
            name=op.f("fk_orders_customer_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
            name=op.f("fk_orders_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
    )

    op.create_table(
        "order_lines",
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "price_per_item", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
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
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_order_lines_order_id_orders"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_order_lines_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("product_id", name=op.f("pk_order_lines")),
    )


def downgrade() -> None:
    op.drop_table("order_lines")
    op.drop_table("orders")

    op.execute("DROP TYPE IF EXISTS deliverypreference")
