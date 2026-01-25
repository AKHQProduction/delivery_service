"""Add shop_delivery_time_slots table and update orders.

Revision ID: 00010
Revises: 00009
Create Date: 2026-01-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00010"
down_revision: str | Sequence[str] | None = "00009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shop_delivery_time_slots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("label", sa.String(100), nullable=True),
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
            "shop_id",
            "start_time",
            "end_time",
            name="uq_shop_delivery_time_slot",
        ),
    )

    op.execute("""
        INSERT INTO shop_delivery_time_slots
            (id, shop_id, start_time, end_time, label)
        SELECT
            gen_random_uuid(), id,
            '09:00:00'::time, '14:00:00'::time,
            'Первая половина дня'
        FROM shops
    """)
    op.execute("""
        INSERT INTO shop_delivery_time_slots
            (id, shop_id, start_time, end_time, label)
        SELECT
            gen_random_uuid(), id,
            '14:00:00'::time, '20:00:00'::time,
            'Вторая половина дня'
        FROM shops
    """)

    op.add_column(
        "orders",
        sa.Column("delivery_start_time", sa.Time(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_end_time", sa.Time(), nullable=True),
    )

    op.execute("""
        UPDATE orders SET
            delivery_start_time = '09:00:00'::time,
            delivery_end_time = '14:00:00'::time
        WHERE time_preference = 'FIRST_HALF'
    """)
    op.execute("""
        UPDATE orders SET
            delivery_start_time = '14:00:00'::time,
            delivery_end_time = '20:00:00'::time
        WHERE time_preference = 'SECOND_HALF'
    """)

    op.alter_column("orders", "delivery_start_time", nullable=False)
    op.alter_column("orders", "delivery_end_time", nullable=False)
    op.drop_column("orders", "time_preference")


def downgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "time_preference",
            sa.String(),
            nullable=True,
        ),
    )

    op.execute("""
        UPDATE orders SET time_preference = 'FIRST_HALF'
        WHERE delivery_start_time = '09:00:00'::time
    """)
    op.execute("""
        UPDATE orders SET time_preference = 'SECOND_HALF'
        WHERE delivery_start_time = '14:00:00'::time
    """)

    op.alter_column("orders", "time_preference", nullable=False)
    op.drop_column("orders", "delivery_end_time")
    op.drop_column("orders", "delivery_start_time")

    op.drop_table("shop_delivery_time_slots")
