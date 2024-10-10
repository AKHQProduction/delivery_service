import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite, relationship

from entities.profile.models import Profile
from entities.profile.value_objects import UserAddress
from infrastructure.persistence.models import mapper_registry

profiles_table = sa.Table(
    "profiles",
    mapper_registry.metadata,
    sa.Column("profiles_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("phone_number", sa.String(13), nullable=True),
    sa.Column("address_city", sa.String, nullable=True),
    sa.Column("address_street", sa.String, nullable=True),
    sa.Column("address_house_number", sa.String, nullable=True),
    sa.Column("address_apartment_number", sa.Integer, nullable=True),
    sa.Column("address_floor", sa.Integer, nullable=True),
    sa.Column("address_intercom_code", sa.Integer, nullable=True),
    sa.Column(
        "shop_id",
        sa.BigInteger,
        sa.ForeignKey("shops.shop_id", ondelete="SET NULL"),
    ),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.user_id", ondelete="CASCADE"),
    ),
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
    UniqueConstraint(
        "user_id", "shop_id", "phone_number", name="uq_phone_user_number"
    ),
)


def map_profile_table() -> None:
    mapper_registry.map_imperatively(
        Profile,
        profiles_table,
        properties={
            "shop": relationship("Shop", back_populates="profile"),
            "user": relationship("User", back_populates="profile"),
            "user_address": composite(
                UserAddress,
                profiles_table.c.address_city,
                profiles_table.c.address_street,
                profiles_table.c.address_house_number,
                profiles_table.c.address_apartment_number,
                profiles_table.c.address_floor,
                profiles_table.c.address_intercom_code,
            ),
        },
    )
