"""Remove custom_id, add FK indexes, unique telegram_id.

Revision ID: 00011
Revises: 00010
Create Date: 2026-01-31

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00011"
down_revision: str | Sequence[str] | None = "00010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE clients SET full_name = custom_id "
        "WHERE custom_id IS NOT NULL AND TRIM(custom_id) != ''"
    )
    op.drop_column("clients", "custom_id")

    op.create_index("ix_orders_shop_id_date", "orders", ["shop_id", "date"])
    op.create_index("ix_orders_client_id", "orders", ["client_id"])
    op.create_index(
        "ix_orders_delivery_start_time", "orders", ["delivery_start_time"]
    )

    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])

    op.create_index("ix_clients_shop_id", "clients", ["shop_id"])
    op.create_index("ix_clients_user_id", "clients", ["user_id"])

    op.create_index(
        "ix_client_phones_client_id", "client_phones", ["client_id"]
    )
    op.create_index("ix_client_phones_shop_id", "client_phones", ["shop_id"])

    op.create_index(
        "ix_client_addresses_client_id", "client_addresses", ["client_id"]
    )

    op.create_index("ix_products_shop_id", "products", ["shop_id"])
    op.create_index("ix_products_category_id", "products", ["category_id"])

    op.create_index(
        "ix_shop_memberships_shop_id", "shop_memberships", ["shop_id"]
    )

    op.create_unique_constraint(
        "uq_telegram_accounts_telegram_id",
        "telegram_accounts",
        ["telegram_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_telegram_accounts_telegram_id", "telegram_accounts", type_="unique"
    )

    op.drop_index("ix_shop_memberships_shop_id", table_name="shop_memberships")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_shop_id", table_name="products")
    op.drop_index(
        "ix_client_addresses_client_id", table_name="client_addresses"
    )
    op.drop_index("ix_client_phones_shop_id", table_name="client_phones")
    op.drop_index("ix_client_phones_client_id", table_name="client_phones")
    op.drop_index("ix_clients_user_id", table_name="clients")
    op.drop_index("ix_clients_shop_id", table_name="clients")
    op.drop_index("ix_order_items_product_id", table_name="order_items")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_index("ix_orders_delivery_start_time", table_name="orders")
    op.drop_index("ix_orders_client_id", table_name="orders")
    op.drop_index("ix_orders_shop_id_date", table_name="orders")

    op.add_column(
        "clients", sa.Column("custom_id", sa.String(), nullable=True)
    )
