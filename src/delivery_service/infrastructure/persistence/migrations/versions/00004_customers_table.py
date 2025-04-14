"""Customers table

Revision ID: 00004
Revises: 00003
Create Date: 2025-04-14 18:10:30.468824

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from delivery_service.domain.customers.phone_number import PhoneBook
from delivery_service.domain.shared.vo.address import DeliveryAddress
from delivery_service.infrastructure.persistence.tables.base import (
    value_object_to_json,
)

revision: str = "00004"
down_revision: Union[str, None] = "00003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("contacts", value_object_to_json(PhoneBook), nullable=True),
        sa.Column(
            "delivery_address",
            value_object_to_json(DeliveryAddress),
            nullable=True,
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
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
            name=op.f("fk_customers_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_customers_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_customers")),
        sa.UniqueConstraint(
            "user_id", "shop_id", name="uq_customers_user_id_shop_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("customers")
