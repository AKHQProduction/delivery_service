"""Shops and staff member tables

Revision ID: 00002
Revises: 00001
Create Date: 2025-04-09 21:54:08.765587

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from delivery_service.domain.shared.vo.location import Coordinates
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.infrastructure.persistence.tables.base import (
    value_object_to_json,
)

revision: str = "00002"
down_revision: Union[str, None] = "00001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shops",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "coordinates", value_object_to_json(Coordinates), nullable=False
        ),
        sa.Column("days_off", value_object_to_json(DaysOff), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shops")),
        sa.UniqueConstraint("id", name=op.f("uq_shops_id")),
    )

    op.create_table(
        "staff_members",
        sa.Column("user_id", sa.UUID(), nullable=True, primary_key=True),
        sa.Column("shop_id", sa.UUID(), nullable=True),
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
            name=op.f("fk_staff_members_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_staff_members_user_id_users"),
            ondelete="CASCADE",
        ),
    )
    sa.UniqueConstraint(
        "user_id", "shop_id", name=op.f("uq_staff_members_user_id_shop_id")
    )
    op.drop_constraint("uq_roles_name", "roles", type_="unique")
    op.create_unique_constraint(op.f("uq_users_id"), "users", ["id"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_users_id"), "users", type_="unique")
    op.create_unique_constraint("uq_roles_name", "roles", ["name"])
    op.drop_table("staff_members")
    op.drop_table("shops")
