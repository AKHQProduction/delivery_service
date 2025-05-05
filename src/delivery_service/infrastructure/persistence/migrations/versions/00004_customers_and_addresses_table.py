"""Customers and addresses table

Revision ID: 00004
Revises: 00003
Create Date: 2025-04-14 18:10:30.468824

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from delivery_service.domain.shared.vo.address import (
    Coordinates,
)
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
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
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
            ["user_id"],
            ["users.id"],
            name=op.f("fk_customers_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customers")),
    )

    op.create_table(
        "addresses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("street", sa.String(), nullable=False),
        sa.Column("house_number", sa.String(), nullable=False),
        sa.Column("apartment_number", sa.String(), nullable=True),
        sa.Column("floor", sa.Integer(), nullable=True),
        sa.Column("intercom_code", sa.String(), nullable=True),
        sa.Column(
            "coordinates", value_object_to_json(Coordinates), nullable=True
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
            ["customer_id"],
            ["customers.id"],
            name=op.f("fk_addresses_customer_id_customers"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
            name=op.f("fk_addresses_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_addresses")),
        sa.UniqueConstraint(
            "shop_id", "city", "street", "house_number", name="uq_user_address"
        ),
    )

    op.create_table(
        "phone_numbers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("number", sa.String(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
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
            name=op.f("fk_phone_numbers_customer_id_customers"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_phone_numbers")),
    )

    op.create_table(
        "customers_shops",
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name=op.f("fk_customers_shops_customer_id_customers"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
            name=op.f("fk_customers_shops_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "customer_id", "shop_id", name=op.f("pk_customers_shops")
        ),
    )


def downgrade() -> None:
    op.drop_table("customers_shops")
    op.drop_table("addresses")
    op.drop_table("phone_numbers")
    op.drop_table("customers")
