import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.application.vars import (
    PaymentMethodId,
    ShopId,
    ShopRepeatOrderMode,
    TimeSlotId,
    UserId,
)
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.categories import Category
    from backend.infrastructure.persistence.tables.clients import Client
    from backend.infrastructure.persistence.tables.districts import District
    from backend.infrastructure.persistence.tables.orders import Order
    from backend.infrastructure.persistence.tables.products import Product
    from backend.infrastructure.persistence.tables.users import User


class Shop(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shops"

    id: Mapped[ShopId] = mapped_column(sa.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    city: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    street: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    house: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(sa.Double, nullable=True)
    longitude: Mapped[float | None] = mapped_column(sa.Double, nullable=True)
    repeat_order_mode: Mapped[ShopRepeatOrderMode] = mapped_column(
        sa.String(32),
        nullable=False,
        default=ShopRepeatOrderMode.CONFIRMATION_REQUIRED,
        server_default=ShopRepeatOrderMode.CONFIRMATION_REQUIRED,
    )

    memberships: Mapped[list["ShopMembership"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    categories: Mapped[list["Category"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    districts: Mapped[list["District"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    clients: Mapped[list["Client"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    delivery_time_slots: Mapped[list["ShopDeliveryTimeSlot"]] = relationship(
        back_populates="shop", lazy="raise"
    )
    payment_methods: Mapped[list["ShopPaymentMethod"]] = relationship(
        back_populates="shop", lazy="raise"
    )

    __table_args__ = (
        CheckConstraint(
            "(latitude IS NULL) = (longitude IS NULL)",
            name="ck_shops_coords_both_or_none",
        ),
    )

    def __repr__(self) -> str:
        return f"<Shop id={self.id} name={self.name}>"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)

    memberships: Mapped[list["ShopMembership"]] = relationship(
        back_populates="role", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Role name={self.name}>"


class ShopMembership(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shop_memberships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    user_id: Mapped[UserId] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE")
    )
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("roles.id"))

    user: Mapped["User"] = relationship(
        back_populates="membership", lazy="raise"
    )
    shop: Mapped["Shop"] = relationship(
        back_populates="memberships", lazy="raise"
    )
    role: Mapped["Role"] = relationship(
        back_populates="memberships", lazy="raise"
    )

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_shop_membership_user"),
    )

    def __repr__(self) -> str:
        return (
            f"<ShopMembership user_id={self.user_id} "
            f"shop_id={self.shop_id} role_id={self.role_id}>"
        )


class ShopDeliveryTimeSlot(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shop_delivery_time_slots"

    id: Mapped[TimeSlotId] = mapped_column(sa.UUID, primary_key=True)
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime.time] = mapped_column(sa.Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(sa.Time, nullable=False)
    label: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    shop: Mapped["Shop"] = relationship(
        back_populates="delivery_time_slots", lazy="raise"
    )

    __table_args__ = (
        UniqueConstraint(
            "shop_id",
            "start_time",
            "end_time",
            name="uq_shop_delivery_time_slot",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ShopDeliveryTimeSlot id={self.id} "
            f"shop_id={self.shop_id} {self.start_time}-{self.end_time}>"
        )


class ShopPaymentMethod(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shop_payment_methods"

    id: Mapped[PaymentMethodId] = mapped_column(sa.UUID, primary_key=True)
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)

    shop: Mapped["Shop"] = relationship(
        back_populates="payment_methods", lazy="raise"
    )

    __table_args__ = (
        UniqueConstraint(
            "shop_id",
            "name",
            name="uq_shop_payment_method",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ShopPaymentMethod id={self.id} "
            f"shop_id={self.shop_id} name={self.name}>"
        )
