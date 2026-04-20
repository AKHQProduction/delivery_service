"""Add balance payment method for all shops.

Revision ID: 00017
Revises: 00016
Create Date: 2026-04-20
"""

from collections.abc import Sequence

from alembic import op

revision: str = "00017"
down_revision: str | Sequence[str] | None = "00016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO shop_payment_methods (id, shop_id, name)
        SELECT gen_random_uuid(), s.id, 'Баланс'
        FROM shops s
        WHERE NOT EXISTS (
            SELECT 1
            FROM shop_payment_methods spm
            WHERE spm.shop_id = s.id
              AND spm.name = 'Баланс'
        )
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM shop_payment_methods
        WHERE name = 'Баланс'
    """)
