"""Drop unique constraint on client phone number per shop.

Revision ID: 00007
Revises: 00006
Create Date: 2025-01-12

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "00007"
down_revision: str | Sequence[str] | None = "00006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_client_phone_per_shop", "client_phones", type_="unique"
    )


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_client_phone_per_shop", "client_phones", ["shop_id", "number"]
    )
