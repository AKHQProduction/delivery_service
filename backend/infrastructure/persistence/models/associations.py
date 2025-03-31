import sqlalchemy as sa

from .base import mapper_registry

association_between_shops_and_users = sa.Table(
    "association_shop_and_users",
    mapper_registry.metadata,
    sa.Column(
        "shop_id",
        sa.BigInteger,
        sa.ForeignKey("shops.shop_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)
