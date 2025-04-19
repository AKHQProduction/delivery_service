import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.orm import composite, relationship

from delivery_service.domain.orders.order import DeliveryPreference, Order
from delivery_service.domain.orders.order_line import OrderLine
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.shared.vo.quantity import Quantity
from delivery_service.infrastructure.persistence.tables.base import (
    MAPPER_REGISTRY,
)

ORDERS_TABLE = sa.Table(
    "orders",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True),
    sa.Column(
        "shop_id",
        sa.ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "customer_id",
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column(
        "delivery_preference", sa.Enum(DeliveryPreference), nullable=False
    ),
    sa.Column("delivery_date", sa.Date, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        nullable=False,
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
        nullable=True,
    ),
)

ORDER_LINES_TABLE = sa.Table(
    "order_lines",
    MAPPER_REGISTRY.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column(
        "order_id",
        sa.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("title", sa.String, nullable=False),
    sa.Column(
        "price_per_item", sa.Numeric(precision=10, scale=2), nullable=False
    ),
    sa.Column("quantity", sa.Integer, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        nullable=False,
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
        nullable=True,
    ),
)

MAPPER_REGISTRY.map_imperatively(
    Order,
    ORDERS_TABLE,
    properties={
        "_entity_id": ORDERS_TABLE.c.id,
        "_shop_id": ORDERS_TABLE.c.shop_id,
        "_customer_id": ORDERS_TABLE.c.customer_id,
        "_delivery_preference": ORDERS_TABLE.c.delivery_preference,
        "_delivery_date": ORDERS_TABLE.c.delivery_date,
        "_order_lines": relationship(
            OrderLine,
            primaryjoin=and_(
                ORDERS_TABLE.c.id == ORDER_LINES_TABLE.c.order_id
            ),
            back_populates="_order",
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
    },
)

MAPPER_REGISTRY.map_imperatively(
    OrderLine,
    ORDER_LINES_TABLE,
    properties={
        "_entity_id": ORDER_LINES_TABLE.c.product_id,
        "_order_id": ORDER_LINES_TABLE.c.order_id,
        "_title": ORDER_LINES_TABLE.c.title,
        "_price_per_item": composite(
            Price, ORDER_LINES_TABLE.c.price_per_item
        ),
        "_quantity": composite(Quantity, ORDER_LINES_TABLE.c.quantity),
        "_order": relationship(
            Order,
            back_populates="_order_lines",
        ),
    },
)
