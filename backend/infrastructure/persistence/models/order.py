import sqlalchemy as sa
from sqlalchemy.orm import composite, relationship

from entities.order.models import Order, OrderItem, OrderStatus
from entities.order.value_objects import OrderItemAmount, OrderTotalPrice
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
    sa.Column("order_total_price", sa.DECIMAL(10, 2), nullable=False),
    sa.Column(
        "user_id",
        sa.BigInteger,
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
            "user": relationship("User", back_populates="order"),
            "shop": relationship("Shop", back_populates="order"),
            "order_item": relationship("OrderItem", back_populates="order"),
            "total_price": composite(
                OrderTotalPrice, orders_table.c.order_total_price
            ),
        },
    )


def map_order_items_table() -> None:
    mapper_registry.map_imperatively(
        OrderItem,
        order_items_table,
        properties={
            "order": relationship("Order", back_populates="order_item"),
            "amount": composite(
                OrderItemAmount,
                order_items_table.c.item_quantity,
                order_items_table.c.price_per_order_item,
            ),
        },
    )
