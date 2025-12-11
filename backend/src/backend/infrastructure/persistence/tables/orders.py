import datetime
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.clients import Client
    from backend.infrastructure.persistence.tables.shops import Shop


class Order(Base, CreatedAt, UpdatedAt):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    delivery_address: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    delivery_phone: Mapped[str] = mapped_column(sa.String, nullable=False)
    time_preference: Mapped[str] = mapped_column(sa.String, nullable=False)
    comment: Mapped[str] = mapped_column(sa.String, nullable=True)

    shop_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )

    shop: Mapped["Shop"] = relationship(back_populates="orders")
    client: Mapped["Client"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Order id={self.id} date={self.date} "
            f"delivery_address={self.delivery_address} "
            f"delivery_phone={self.delivery_phone}"
        )


class OrderItem(Base, CreatedAt, UpdatedAt):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        sa.BIGINT, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    price_per_item: Mapped[int] = mapped_column(
        sa.Numeric(precision=10, scale=2), nullable=False
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem id={self.id} name={self.name} "
            f"quantity={self.quantity} price={self.price_per_item}>"
        )
