import sqlalchemy as sa
from sqlalchemy.orm import composite, relationship

from entities.user.models import User
from entities.user.value_objects import UserAddress
from infrastructure.persistence.models import mapper_registry
from infrastructure.persistence.models.associations import (
    association_between_shops_and_users,
)

users_table = sa.Table(
    "users",
    mapper_registry.metadata,
    sa.Column(
        "user_id",
        sa.Integer,
        primary_key=True,
        unique=True,
        autoincrement=True,
        index=True,
    ),
    sa.Column("full_name", sa.String(128), nullable=False),
    sa.Column("tg_id", sa.BigInteger, nullable=True),
    sa.Column(
        "username",
        sa.String(255),
        nullable=True,
        default=None,
    ),
    sa.Column("phone_number", sa.String(13), nullable=True, unique=True),
    sa.Column("address_city", sa.String, nullable=True),
    sa.Column("address_street", sa.String, nullable=True),
    sa.Column("address_house_number", sa.String, nullable=True),
    sa.Column("address_apartment_number", sa.Integer, nullable=True),
    sa.Column("address_floor", sa.Integer, nullable=True),
    sa.Column("address_intercom_code", sa.Integer, nullable=True),
    sa.Column("is_active", sa.Boolean, default=True, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "shops": relationship(
                "Shop",
                secondary=association_between_shops_and_users,
                back_populates="users",
            ),
            "employees": relationship(
                "Employee",
                back_populates="user",
                cascade="all, delete-orphan",
            ),
            "order": relationship(
                "Order", back_populates="user", cascade="all, delete-orphan"
            ),
            "oid": users_table.c.user_id,
            "user_address": composite(
                UserAddress,
                users_table.c.address_city,
                users_table.c.address_street,
                users_table.c.address_house_number,
                users_table.c.address_apartment_number,
                users_table.c.address_floor,
                users_table.c.address_intercom_code,
            ),
        },
    )
