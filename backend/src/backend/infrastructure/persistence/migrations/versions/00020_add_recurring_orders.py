"""Add recurring orders.

Revision ID: 00020
Revises: 00019
Create Date: 2026-05-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, ENUM

revision: str = "00020"
down_revision: str | Sequence[str] | None = "00019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    schedule_type = ENUM(
        "WEEKLY",
        "MONTHLY_BY_DAY",
        name="schedule_type",
        create_type=False,
    )
    recurring_order_status = ENUM(
        "ACTIVE",
        "PAUSED",
        name="recurring_order_status",
        create_type=False,
    )
    recurring_order_occurrence_status = ENUM(
        "SCHEDULED",
        "CANCELLED",
        name="recurring_order_occurrence_status",
        create_type=False,
    )
    schedule_type.create(op.get_bind(), checkfirst=True)
    recurring_order_status.create(op.get_bind(), checkfirst=True)
    recurring_order_occurrence_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "recurring_orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("address_id", sa.Integer(), nullable=True),
        sa.Column("phone_id", sa.Integer(), nullable=True),
        sa.Column("time_slot_id", sa.UUID(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("schedule_type", schedule_type, nullable=False),
        sa.Column("weekdays", ARRAY(sa.SmallInteger()), nullable=True),
        sa.Column("month_days", ARRAY(sa.SmallInteger()), nullable=True),
        sa.Column(
            "status",
            recurring_order_status,
            server_default="ACTIVE",
            nullable=False,
        ),
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
        sa.CheckConstraint(
            """
            (
                schedule_type = 'WEEKLY'
                AND weekdays IS NOT NULL
                AND cardinality(weekdays) > 0
                AND weekdays <@ ARRAY[1,2,3,4,5,6,7]::smallint[]
                AND month_days IS NULL
            )
            OR
            (
                schedule_type = 'MONTHLY_BY_DAY'
                AND month_days IS NOT NULL
                AND cardinality(month_days) > 0
                AND month_days <@ ARRAY[
                    1,2,3,4,5,6,7,8,9,10,
                    11,12,13,14,15,16,17,18,19,20,
                    21,22,23,24,25,26,27,28,29,30,31
                ]::smallint[]
                AND weekdays IS NULL
            )
            """,
            name="ck_recurring_orders_schedule_payload",
        ),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["client_id"], ["clients.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["address_id"], ["client_addresses.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["phone_id"], ["client_phones.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["time_slot_id"],
            ["shop_delivery_time_slots.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recurring_orders_shop_client",
        "recurring_orders",
        ["shop_id", "client_id"],
    )
    op.create_index(
        "ix_recurring_orders_shop_status",
        "recurring_orders",
        ["shop_id", "status"],
    )
    op.create_index(
        "ix_recurring_orders_weekdays",
        "recurring_orders",
        ["weekdays"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_recurring_orders_month_days",
        "recurring_orders",
        ["month_days"],
        postgresql_using="gin",
    )

    op.create_table(
        "recurring_order_items",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("recurring_order_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
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
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="ck_recurring_items_quantity"),
        sa.ForeignKeyConstraint(
            ["recurring_order_id"],
            ["recurring_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recurring_order_items_recurring_order",
        "recurring_order_items",
        ["recurring_order_id"],
    )

    op.create_table(
        "recurring_order_occurrences",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("recurring_order_id", sa.UUID(), nullable=False),
        sa.Column("scheduled_for", sa.Date(), nullable=False),
        sa.Column("status", recurring_order_occurrence_status, nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=True),
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
        sa.CheckConstraint(
            """
            (
                status = 'SCHEDULED'
                AND order_id IS NOT NULL
            )
            OR
            (
                status = 'CANCELLED'
                AND order_id IS NULL
            )
            """,
            name="ck_recurring_order_occurrences_status_order",
        ),
        sa.ForeignKeyConstraint(
            ["recurring_order_id"],
            ["recurring_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "recurring_order_id",
            "scheduled_for",
            name="uq_recurring_order_occurrences_schedule",
        ),
    )
    op.create_index(
        "ix_recurring_order_occurrences_recurring_order",
        "recurring_order_occurrences",
        ["recurring_order_id"],
    )

    op.add_column(
        "orders",
        sa.Column("recurring_order_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("time_slot_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "orders_recurring_order_id_fkey",
        "orders",
        "recurring_orders",
        ["recurring_order_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "orders_time_slot_id_fkey",
        "orders",
        "shop_delivery_time_slots",
        ["time_slot_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_orders_recurring_order_id",
        "orders",
        ["recurring_order_id"],
    )
    op.create_index(
        "ix_orders_time_slot_id",
        "orders",
        ["time_slot_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_orders_time_slot_id", table_name="orders")
    op.drop_index("ix_orders_recurring_order_id", table_name="orders")
    op.drop_constraint(
        "orders_time_slot_id_fkey", "orders", type_="foreignkey"
    )
    op.drop_constraint(
        "orders_recurring_order_id_fkey", "orders", type_="foreignkey"
    )
    op.drop_column("orders", "time_slot_id")
    op.drop_column("orders", "recurring_order_id")

    op.drop_index(
        "ix_recurring_order_occurrences_recurring_order",
        table_name="recurring_order_occurrences",
    )
    op.drop_table("recurring_order_occurrences")

    op.drop_index(
        "ix_recurring_order_items_recurring_order",
        table_name="recurring_order_items",
    )
    op.drop_table("recurring_order_items")

    op.drop_index(
        "ix_recurring_orders_month_days", table_name="recurring_orders"
    )
    op.drop_index(
        "ix_recurring_orders_weekdays", table_name="recurring_orders"
    )
    op.drop_index(
        "ix_recurring_orders_shop_status", table_name="recurring_orders"
    )
    op.drop_index(
        "ix_recurring_orders_shop_client", table_name="recurring_orders"
    )
    op.drop_table("recurring_orders")

    sa.Enum(name="recurring_order_occurrence_status").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(name="recurring_order_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="schedule_type").drop(op.get_bind(), checkfirst=True)
