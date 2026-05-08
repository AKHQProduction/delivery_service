from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PhoneId,
    ProductId,
    RecurringOrderId,
    RecurringOrderItemId,
    RecurringOrderOccurrenceId,
    RecurringOrderOccurrenceStatus,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    TimeSlotId,
)
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.orders import Order
    from backend.infrastructure.persistence.tables.products import Product


class RecurringOrder(Base, CreatedAt, UpdatedAt):
    __tablename__ = "recurring_orders"

    id: Mapped[RecurringOrderId] = mapped_column(sa.UUID, primary_key=True)
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[ClientId] = mapped_column(
        sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    address_id: Mapped[AddressId | None] = mapped_column(
        sa.ForeignKey("client_addresses.id", ondelete="SET NULL"),
        nullable=True,
    )
    phone_id: Mapped[PhoneId | None] = mapped_column(
        sa.ForeignKey("client_phones.id", ondelete="SET NULL"),
        nullable=True,
    )
    time_slot_id: Mapped[TimeSlotId] = mapped_column(
        sa.ForeignKey("shop_delivery_time_slots.id", ondelete="CASCADE"),
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(sa.String, nullable=False)
    comment: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    schedule_type: Mapped[ScheduleType] = mapped_column(
        sa.Enum(ScheduleType, name="schedule_type"),
        nullable=False,
    )
    weekdays: Mapped[list[int] | None] = mapped_column(
        MutableList.as_mutable(ARRAY(sa.SmallInteger)), nullable=True
    )
    month_days: Mapped[list[int] | None] = mapped_column(
        MutableList.as_mutable(ARRAY(sa.SmallInteger)), nullable=True
    )
    status: Mapped[RecurringOrderStatus] = mapped_column(
        sa.Enum(RecurringOrderStatus, name="recurring_order_status"),
        nullable=False,
        default=RecurringOrderStatus.ACTIVE,
        server_default=RecurringOrderStatus.ACTIVE.value,
    )

    items: Mapped[list["RecurringOrderItem"]] = relationship(
        back_populates="recurring_order",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    occurrences: Mapped[list["RecurringOrderOccurrence"]] = relationship(
        back_populates="recurring_order",
        cascade="all, delete-orphan",
        lazy="raise",
    )


class RecurringOrderItem(Base, CreatedAt, UpdatedAt):
    __tablename__ = "recurring_order_items"

    id: Mapped[RecurringOrderItemId] = mapped_column(
        sa.BIGINT, primary_key=True, autoincrement=True
    )
    recurring_order_id: Mapped[RecurringOrderId] = mapped_column(
        sa.ForeignKey("recurring_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[ProductId] = mapped_column(
        sa.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    recurring_order: Mapped[RecurringOrder] = relationship(
        back_populates="items", lazy="raise"
    )
    product: Mapped["Product"] = relationship(lazy="raise")


class RecurringOrderOccurrence(Base, CreatedAt, UpdatedAt):
    __tablename__ = "recurring_order_occurrences"

    id: Mapped[RecurringOrderOccurrenceId] = mapped_column(
        sa.BIGINT, primary_key=True, autoincrement=True
    )
    recurring_order_id: Mapped[RecurringOrderId] = mapped_column(
        sa.ForeignKey("recurring_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    scheduled_for: Mapped[date] = mapped_column(sa.Date, nullable=False)
    status: Mapped[RecurringOrderOccurrenceStatus] = mapped_column(
        sa.Enum(
            RecurringOrderOccurrenceStatus,
            name="recurring_order_occurrence_status",
        ),
        nullable=False,
    )
    order_id: Mapped["OrderId | None"] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )

    recurring_order: Mapped[RecurringOrder] = relationship(
        back_populates="occurrences", lazy="raise"
    )
    order: Mapped["Order | None"] = relationship(lazy="raise")

    __table_args__ = (
        sa.UniqueConstraint(
            "recurring_order_id",
            "scheduled_for",
            name="uq_recurring_order_occurrences_schedule",
        ),
        sa.CheckConstraint(
            """
            (
                status = 'SCHEDULED'
                AND order_id IS NOT NULL
            )
            OR
            (
                status = 'CANCELLED'
                AND order_id IS NULL
            )
            """,
            name="ck_recurring_order_occurrences_status_order",
        ),
    )
