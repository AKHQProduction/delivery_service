import sqlalchemy as sa
from sqlalchemy.orm import composite, relationship

from entities.goods.models import Goods, GoodsType
from entities.goods.value_objects import GoodsPrice, GoodsTitle
from infrastructure.persistence.models import mapper_registry

goods_table = sa.Table(
    "goods",
    mapper_registry.metadata,
    sa.Column("goods_id", sa.UUID, primary_key=True, unique=True),
    sa.Column(
        "shop_id",
        sa.BigInteger,
        sa.ForeignKey("shops.shop_id", ondelete="CASCADE"),
    ),
    sa.Column("goods_title", sa.String(length=20), nullable=False),
    sa.Column("goods_price", sa.DECIMAL(10, 2), nullable=False),
    sa.Column("goods_type", sa.Enum(GoodsType), nullable=False),
    sa.Column("metadata_path", sa.String(), nullable=True),
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


def map_goods_table() -> None:
    mapper_registry.map_imperatively(
        Goods,
        goods_table,
        properties={
            "shop": relationship("Shop", back_populates="goods"),
            "title": composite(GoodsTitle, goods_table.c.goods_title),
            "price": composite(GoodsPrice, goods_table.c.goods_price),
        },
    )
