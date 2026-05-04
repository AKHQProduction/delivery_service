"""Move preferred time slot to client addresses.

Revision ID: 00019
Revises: 00018
Create Date: 2026-05-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00019"
down_revision: str | Sequence[str] | None = "00018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADDRESS_CONSTRAINT_NAME = "client_addresses_preferred_time_slot_id_fkey"
CLIENT_CONSTRAINT_NAME = (
    "fk_clients_preferred_time_slot_id_shop_delivery_time_slots"
)


def upgrade() -> None:
    op.add_column(
        "client_addresses",
        sa.Column("preferred_time_slot_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        ADDRESS_CONSTRAINT_NAME,
        "client_addresses",
        "shop_delivery_time_slots",
        ["preferred_time_slot_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        sa.text(
            """
            WITH first_addresses AS (
                SELECT DISTINCT ON (client_id)
                    id,
                    client_id
                FROM client_addresses
                ORDER BY client_id, is_primary DESC, id ASC
            )
            UPDATE client_addresses AS address
            SET preferred_time_slot_id = client.preferred_time_slot_id
            FROM clients AS client
            JOIN first_addresses AS first_address
                ON first_address.client_id = client.id
            WHERE address.id = first_address.id
              AND client.preferred_time_slot_id IS NOT NULL
            """
        )
    )

    op.drop_constraint(CLIENT_CONSTRAINT_NAME, "clients", type_="foreignkey")
    op.drop_column("clients", "preferred_time_slot_id")


def downgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("preferred_time_slot_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        CLIENT_CONSTRAINT_NAME,
        "clients",
        "shop_delivery_time_slots",
        ["preferred_time_slot_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        sa.text(
            """
            UPDATE clients AS client
            SET preferred_time_slot_id = address.preferred_time_slot_id
            FROM client_addresses AS address
            WHERE address.client_id = client.id
              AND address.preferred_time_slot_id IS NOT NULL
              AND address.id = (
                  SELECT inner_address.id
                  FROM client_addresses AS inner_address
                  WHERE inner_address.client_id = client.id
                    AND inner_address.preferred_time_slot_id IS NOT NULL
                  ORDER BY inner_address.is_primary DESC, inner_address.id ASC
                  LIMIT 1
              )
            """
        )
    )

    op.drop_constraint(
        ADDRESS_CONSTRAINT_NAME, "client_addresses", type_="foreignkey"
    )
    op.drop_column("client_addresses", "preferred_time_slot_id")
