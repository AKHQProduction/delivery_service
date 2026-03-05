import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from backend.application.vars import RouteEdgeHistoryId, ShopId
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)


class RouteEdgeHistory(Base, CreatedAt, UpdatedAt):
    __tablename__ = "route_edge_history"

    id: Mapped[RouteEdgeHistoryId] = mapped_column(sa.UUID, primary_key=True)
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    from_coords: Mapped[list[float]] = mapped_column(
        ARRAY(sa.Double), nullable=False
    )
    to_coords: Mapped[list[float]] = mapped_column(
        ARRAY(sa.Double), nullable=False
    )
    times_seen: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=1, server_default=sa.text("1")
    )
    last_seen: Mapped[datetime.datetime] = mapped_column(
        sa.TIMESTAMP, nullable=False, server_default=sa.func.now()
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "shop_id",
            "from_coords",
            "to_coords",
            name="uq_route_edge_shop_coords",
        ),
        sa.Index(
            "ix_route_edge_shop_last_seen",
            "shop_id",
            "last_seen",
        ),
    )
