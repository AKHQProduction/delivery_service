"""Add shop_payment_methods table and migrate order payment_method values.

Revision ID: 00015
Revises: 00014
Create Date: 2026-04-03

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00015"
down_revision: str | Sequence[str] | None = "00014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shop_payment_methods",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
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
            "name",
            name="uq_shop_payment_method",
        ),
    )

    op.execute("""
        INSERT INTO shop_payment_methods (id, shop_id, name)
        SELECT gen_random_uuid(), id, 'Готівка' FROM shops
    """)
    op.execute("""
        INSERT INTO shop_payment_methods (id, shop_id, name)
        SELECT gen_random_uuid(), id, 'На рахунок' FROM shops
    """)
    op.execute("""
        INSERT INTO shop_payment_methods (id, shop_id, name)
        SELECT gen_random_uuid(), id, 'Інше' FROM shops
    """)

    op.execute("""
        UPDATE orders SET payment_method = 'Готівка'
        WHERE payment_method = 'CASH'
    """)
    op.execute("""
        UPDATE orders SET payment_method = 'На рахунок'
        WHERE payment_method = 'BANK_TRANSFER'
    """)
    op.execute("""
        UPDATE orders SET payment_method = 'Інше'
        WHERE payment_method = 'OTHER'
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE orders SET payment_method = 'CASH'
        WHERE payment_method = 'Готівка'
    """)
    op.execute("""
        UPDATE orders SET payment_method = 'BANK_TRANSFER'
        WHERE payment_method = 'На рахунок'
    """)
    op.execute("""
        UPDATE orders SET payment_method = 'OTHER'
        WHERE payment_method = 'Інше'
    """)

    op.drop_table("shop_payment_methods")
