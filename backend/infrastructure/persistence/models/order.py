import sqlalchemy as sa
from sqlalchemy.orm import composite, relationship

from entities.common.vo import Price, Quantity
from entities.order.models import (
    DeliveryPreference,
    Order,
    OrderItem,
    OrderStatus,
)
from infrastructure.persistence.models import mapper_registry

orders_table = sa.Table(
    "orders",
    mapper_registry.metadata,
    sa.Column("order_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "status",
        sa.Enum(OrderStatus),
        default=OrderStatus.NEW,
    ),
    sa.Column("bottles_quantity", sa.Integer, nullable=False),
    sa.Column(
        "delivery_preference", sa.Enum(DeliveryPreference), nullable=False
    ),
    sa.Column("delivery_date", sa.DATE, nullable=False),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id", ondelete="CASCADE"),
    ),
    sa.Column(
        "shop_id",
        sa.BigInteger,
        sa.ForeignKey("shops.shop_id", ondelete="CASCADE"),
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
)

order_items_table = sa.Table(
    "order_items",
    mapper_registry.metadata,
    sa.Column(
        "order_item_id", sa.Integer, primary_key=True, autoincrement=True
    ),
    sa.Column("order_item_title", sa.String, nullable=False),
    sa.Column("item_quantity", sa.Integer, nullable=False),
    sa.Column("price_per_order_item", sa.DECIMAL(10, 2), nullable=False),
    sa.Column(
        "order_id",
        sa.Integer,
        sa.ForeignKey("orders.order_id", ondelete="CASCADE"),
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
)


def map_orders_table() -> None:
    mapper_registry.map_imperatively(
        Order,
        orders_table,
        properties={
            "oid": orders_table.c.order_id,
            "user": relationship("User", back_populates="order"),
            "shop": relationship("Shop", back_populates="order"),
            "order_item": relationship(
                "OrderItem", back_populates="order", lazy="selectin"
            ),
            "bottles_to_exchange": composite(
                Quantity, orders_table.c.bottles_quantity
            ),
        },
    )


def map_order_items_table() -> None:
    mapper_registry.map_imperatively(
        OrderItem,
        order_items_table,
        properties={
            "oid": order_items_table.c.order_item_id,
            "order": relationship("Order", back_populates="order_item"),
            "quantity": composite(Quantity, order_items_table.c.item_quantity),
            "price_per_item": composite(
                Price,
                order_items_table.c.price_per_order_item,
            ),
        },
    )
