import sqlalchemy as sa
from sqlalchemy.orm import composite, relationship

from entities.shop.models import Shop
from entities.shop.value_objects import (
    DeliveryDistance,
    RegularDaysOff,
    ShopLocation,
    ShopTitle,
    ShopToken,
    SpecialDaysOff,
)
from infrastructure.persistence.models import mapper_registry
from infrastructure.persistence.models.associations import (
    association_between_shops_and_users,
)

shops_table = sa.Table(
    "shops",
    mapper_registry.metadata,
    sa.Column("shop_id", sa.BigInteger, primary_key=True, unique=True),
    sa.Column("shop_title", sa.String(128), nullable=False),
    sa.Column("shop_token", sa.String(128), nullable=False),
    sa.Column("shop_delivery_distance", sa.Integer, nullable=False),
    sa.Column("location_latitude", sa.Float, nullable=False),
    sa.Column("location_longitude", sa.Float, nullable=False),
    sa.Column("shop_regular_days_off", sa.ARRAY(sa.Integer), default=list),
    sa.Column("shop_special_days_off", sa.ARRAY(sa.DATE), default=list),
    sa.Column("is_active", sa.Boolean, nullable=False, default=True),
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


def map_shops_table() -> None:
    mapper_registry.map_imperatively(
        Shop,
        shops_table,
        properties={
            "users": relationship(
                "User",
                secondary=association_between_shops_and_users,
                back_populates="shops",
                lazy="selectin",
            ),
            "employees": relationship(
                "Employee",
                back_populates="shop",
                cascade="all, delete-orphan",
            ),
            "goods": relationship(
                "Goods", back_populates="shop", cascade="all, delete-orphan"
            ),
            "order": relationship(
                "Order",
                back_populates="shop",
                cascade="all, delete-orphan",
            ),
            "profile": relationship(
                "Profile", back_populates="shop", cascade="all"
            ),
            "title": composite(ShopTitle, shops_table.c.shop_title),
            "token": composite(ShopToken, shops_table.c.shop_token),
            "delivery_distance": composite(
                DeliveryDistance, shops_table.c.shop_delivery_distance
            ),
            "location": composite(
                ShopLocation,
                shops_table.c.location_latitude,
                shops_table.c.location_longitude,
            ),
            "regular_days_off": composite(
                RegularDaysOff,
                shops_table.c.shop_regular_days_off,
            ),
            "special_days_off": composite(
                SpecialDaysOff, shops_table.c.shop_special_days_off
            ),
        },
    )
