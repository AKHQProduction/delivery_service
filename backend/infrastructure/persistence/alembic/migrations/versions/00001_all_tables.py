"""All tables

Revision ID: 00001
Revises:
Create Date: 2024-12-09 22:22:12.492938

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "00001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shops",
        sa.Column("shop_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("delivery_distance", sa.Integer(), nullable=False),
        sa.Column("location_latitude", sa.Float(), nullable=False),
        sa.Column("location_longitude", sa.Float(), nullable=False),
        sa.Column("regular_days_off", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("special_days_off", sa.ARRAY(sa.DATE()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("shop_id", name=op.f("pk_shops")),
        sa.UniqueConstraint("shop_id", name=op.f("uq_shops_shop_id")),
        sa.UniqueConstraint("token", name=op.f("uq_shops_token")),
    )

    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("tg_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=13), nullable=True),
        sa.Column("address_city", sa.String(), nullable=True),
        sa.Column("address_street", sa.String(), nullable=True),
        sa.Column("address_house_number", sa.String(), nullable=True),
        sa.Column("address_apartment_number", sa.Integer(), nullable=True),
        sa.Column("address_floor", sa.Integer(), nullable=True),
        sa.Column("address_intercom_code", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_users")),
        sa.UniqueConstraint(
            "phone_number", name=op.f("uq_users_phone_number")
        ),
    )
    op.create_index(
        op.f("ix_users_user_id"), "users", ["user_id"], unique=True
    )

    op.create_table(
        "association_shop_and_users",
        sa.Column("shop_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.shop_id"],
            name=op.f("fk_association_shop_and_users_shop_id_shops"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_association_shop_and_users_user_id_users"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "shop_id", "user_id", name=op.f("pk_association_shop_and_users")
        ),
    )

    op.create_table(
        "employees",
        sa.Column(
            "employee_id", sa.Integer(), autoincrement=True, nullable=False
        ),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("shop_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "MANAGER", "DRIVER", name="employeerole"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.shop_id"],
            name=op.f("fk_employees_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_employees_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("employee_id", name=op.f("pk_employees")),
        sa.UniqueConstraint("user_id", name="uq_shop_employee"),
    )

    op.create_table(
        "goods",
        sa.Column("goods_id", sa.UUID(), nullable=False),
        sa.Column("shop_id", sa.BigInteger(), nullable=True),
        sa.Column("goods_title", sa.String(length=20), nullable=False),
        sa.Column(
            "goods_price", sa.DECIMAL(precision=10, scale=2), nullable=False
        ),
        sa.Column(
            "goods_type",
            sa.Enum("WATER", "OTHER", name="goodstype"),
            nullable=False,
        ),
        sa.Column("metadata_path", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.shop_id"],
            name=op.f("fk_goods_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("goods_id", name=op.f("pk_goods")),
        sa.UniqueConstraint("goods_id", name=op.f("uq_goods_goods_id")),
    )

    op.create_table(
        "orders",
        sa.Column(
            "order_id", sa.Integer(), autoincrement=True, nullable=False
        ),
        sa.Column("status", sa.Enum("NEW", name="orderstatus"), nullable=True),
        sa.Column(
            "order_total_price",
            sa.DECIMAL(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "bottles_quantity_to_exchange", sa.Integer(), nullable=False
        ),
        sa.Column(
            "delivery_preference",
            sa.Enum("MORNING", "AFTERNOON", name="deliverypreference"),
            nullable=False,
        ),
        sa.Column("delivery_date", sa.DATE(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("shop_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.shop_id"],
            name=op.f("fk_orders_shop_id_shops"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_orders_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("order_id", name=op.f("pk_orders")),
    )

    op.create_table(
        "order_items",
        sa.Column(
            "order_item_id", sa.Integer(), autoincrement=True, nullable=False
        ),
        sa.Column("order_item_title", sa.String(), nullable=False),
        sa.Column("item_quantity", sa.Integer(), nullable=False),
        sa.Column(
            "price_per_order_item",
            sa.DECIMAL(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.order_id"],
            name=op.f("fk_order_items_order_id_orders"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("order_item_id", name=op.f("pk_order_items")),
    )


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("goods")
    op.drop_table("employees")
    op.drop_table("association_shop_and_users")
    op.drop_index(op.f("ix_users_user_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("shops")

    op.execute("DROP TYPE IF EXISTS graphextractionstatusenum")
    op.execute("DROP TYPE IF EXISTS deliverypreference")
    op.execute("DROP TYPE IF EXISTS goodstype")
    op.execute("DROP TYPE IF EXISTS employeerole")
    op.execute("DROP TYPE IF EXISTS orderstatus")
