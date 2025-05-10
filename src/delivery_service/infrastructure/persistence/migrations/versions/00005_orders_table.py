"""Orders table

Revision ID: 00005
Revises: 00004
Create Date: 2025-04-21 18:22:58.788232

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from delivery_service.domain.orders.value_object import TimeSlot
from delivery_service.infrastructure.persistence.tables.base import (
    value_object_to_json,
)

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
        sa.Column("address_id", sa.UUID(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column(
            "time_slot",
            value_object_to_json(TimeSlot),
            nullable=False,
        ),
        sa.Column("note", sa.String, nullable=True),
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
            ["customers.id"],
            name=op.f("fk_orders_customer_id_customers"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
            name=op.f("fk_orders_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["addresses.id"],
            name=op.f("fk_orders_address_id_addresses"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
    )

    op.create_table(
        "order_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_lines")),
    )


def downgrade() -> None:
    op.drop_table("order_lines")
    op.drop_table("orders")
