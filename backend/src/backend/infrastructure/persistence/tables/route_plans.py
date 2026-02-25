import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.application.vars import OrderId, RoutePlanId, ShopId, TimeSlotId
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)


class RoutePlan(Base, CreatedAt, UpdatedAt):
    __tablename__ = "route_plans"

    id: Mapped[RoutePlanId] = mapped_column(sa.UUID, primary_key=True)
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    delivery_date: Mapped[datetime.date] = mapped_column(
        sa.Date, nullable=False
    )
    time_slot_id: Mapped[TimeSlotId | None] = mapped_column(
        sa.ForeignKey("shop_delivery_time_slots.id", ondelete="SET NULL"),
        nullable=True,
    )
    order_sequence: Mapped[list[OrderId]] = mapped_column(
        ARRAY(sa.UUID), nullable=False, default=list
    )
    coordinates_snapshot: Mapped[dict[str, list[float]] | None] = (
        mapped_column(JSONB, nullable=True)
    )

    __table_args__ = (
        sa.Index(
            "ix_route_plans_shop_date_slot",
            "shop_id",
            "delivery_date",
            "time_slot_id",
            unique=True,
            postgresql_where=sa.text("time_slot_id IS NOT NULL"),
        ),
        sa.Index(
            "ix_route_plans_shop_date_no_slot",
            "shop_id",
            "delivery_date",
            unique=True,
            postgresql_where=sa.text("time_slot_id IS NULL"),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<RoutePlan id={self.id} shop_id={self.shop_id} "
            f"date={self.delivery_date}>"
        )
