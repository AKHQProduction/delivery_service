"""Remove custom_id, add FK indexes, unique telegram_id, JSON to JSONB.

Revision ID: 00011
Revises: 00010
Create Date: 2026-01-31

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "00011"
down_revision: str | Sequence[str] | None = "00010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    has_custom_id = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'clients' AND column_name = 'custom_id'"
        )
    ).scalar()

    if has_custom_id:
        op.execute(
            "UPDATE clients SET full_name = custom_id "
            "WHERE custom_id IS NOT NULL AND TRIM(custom_id) != ''"
        )
        op.drop_column("clients", "custom_id")

    op.alter_column(
        "orders",
        "delivery_address",
        type_=JSONB,
        existing_type=sa.JSON(),
        existing_nullable=False,
        postgresql_using="delivery_address::jsonb",
    )

    op.execute("COMMIT")

    _create_index_if_not_exists(
        "ix_orders_shop_id_date", "orders", ["shop_id", "date"]
    )
    _create_index_if_not_exists("ix_orders_client_id", "orders", ["client_id"])
    _create_index_if_not_exists(
        "ix_orders_delivery_start_time", "orders", ["delivery_start_time"]
    )
    _create_index_if_not_exists(
        "ix_order_items_order_id", "order_items", ["order_id"]
    )
    _create_index_if_not_exists(
        "ix_order_items_product_id", "order_items", ["product_id"]
    )
    _create_index_if_not_exists("ix_clients_shop_id", "clients", ["shop_id"])
    _create_index_if_not_exists("ix_clients_user_id", "clients", ["user_id"])
    _create_index_if_not_exists(
        "ix_client_phones_client_id", "client_phones", ["client_id"]
    )
    _create_index_if_not_exists(
        "ix_client_phones_shop_id", "client_phones", ["shop_id"]
    )
    _create_index_if_not_exists(
        "ix_client_addresses_client_id", "client_addresses", ["client_id"]
    )
    _create_index_if_not_exists("ix_products_shop_id", "products", ["shop_id"])
    _create_index_if_not_exists(
        "ix_products_category_id", "products", ["category_id"]
    )
    _create_index_if_not_exists(
        "ix_shop_memberships_shop_id", "shop_memberships", ["shop_id"]
    )
    _create_index_if_not_exists(
        "uq_telegram_accounts_telegram_id",
        "telegram_accounts",
        ["telegram_id"],
        unique=True,
    )


def _create_index_if_not_exists(
    name: str,
    table: str,
    columns: list[str],
    *,
    unique: bool = False,
) -> None:
    conn = op.get_bind()
    exists = conn.execute(
        sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :name"),
        {"name": name},
    ).scalar()
    if exists:
        return
    unique_clause = "UNIQUE " if unique else ""
    cols = ", ".join(columns)
    op.execute(
        f"CREATE {unique_clause}INDEX CONCURRENTLY {name} ON {table} ({cols})"
    )


def downgrade() -> None:
    op.execute("COMMIT")

    op.execute(
        "DROP INDEX CONCURRENTLY IF EXISTS uq_telegram_accounts_telegram_id"
    )
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_shop_memberships_shop_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_products_category_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_products_shop_id")
    op.execute(
        "DROP INDEX CONCURRENTLY IF EXISTS ix_client_addresses_client_id"
    )
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_client_phones_shop_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_client_phones_client_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_clients_user_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_clients_shop_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_order_items_product_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_order_items_order_id")
    op.execute(
        "DROP INDEX CONCURRENTLY IF EXISTS ix_orders_delivery_start_time"
    )
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_orders_client_id")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_orders_shop_id_date")

    op.execute("BEGIN")

    op.add_column(
        "clients", sa.Column("custom_id", sa.String(), nullable=True)
    )

    op.alter_column(
        "orders",
        "delivery_address",
        type_=sa.JSON(),
        existing_type=JSONB,
        existing_nullable=False,
    )
