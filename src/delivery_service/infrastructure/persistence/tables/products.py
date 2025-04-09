import sqlalchemy as sa
from sqlalchemy.orm import composite

from delivery_service.domain.products.product import Product, ProductType
from delivery_service.domain.shared.vo.price import Price
from delivery_service.infrastructure.persistence.tables.base import (
    MAPPER_REGISTRY,
)

PRODUCTS_TABLE = sa.Table(
    "products",
    MAPPER_REGISTRY.metadata,
    sa.Column("id", sa.UUID, primary_key=True, unique=True),
    sa.Column(
        "shop_id", sa.UUID, sa.ForeignKey("shops.id", ondelete="CASCADE")
    ),
    sa.Column("title", sa.String, nullable=False),
    sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column("product_type", sa.Enum(ProductType), nullable=False),
    sa.Column("metadata_path", sa.String, nullable=True),
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
    Product,
    PRODUCTS_TABLE,
    properties={
        "_entity_id": PRODUCTS_TABLE.c.id,
        "_shop_id": PRODUCTS_TABLE.c.shop_id,
        "_title": PRODUCTS_TABLE.c.title,
        "_price": composite(Price, PRODUCTS_TABLE.c.price),
        "_product_type": PRODUCTS_TABLE.c.product_type,
        "_metadata_path": PRODUCTS_TABLE.c.metadata_path,
    },
)
