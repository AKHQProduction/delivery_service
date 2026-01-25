import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.categories import Category
    from backend.infrastructure.persistence.tables.clients import Client
    from backend.infrastructure.persistence.tables.orders import Order
    from backend.infrastructure.persistence.tables.products import Product
    from backend.infrastructure.persistence.tables.users import User


class Shop(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shops"

    id: Mapped[UUID] = mapped_column(sa.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    memberships: Mapped[list["ShopMembership"]] = relationship(
        back_populates="shop"
    )
    products: Mapped[list["Product"]] = relationship(back_populates="shop")
    categories: Mapped[list["Category"]] = relationship(back_populates="shop")
    clients: Mapped[list["Client"]] = relationship(back_populates="shop")
    orders: Mapped[list["Order"]] = relationship(back_populates="shop")
    delivery_time_slots: Mapped[list["ShopDeliveryTimeSlot"]] = relationship(
        back_populates="shop"
    )

    def __repr__(self) -> str:
        return f"<Shop id={self.id} name={self.name}>"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)

    memberships: Mapped[list["ShopMembership"]] = relationship(
        back_populates="role"
    )

    def __repr__(self) -> str:
        return f"<Role name={self.name}>"


class ShopMembership(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shop_memberships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    shop_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE")
    )
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("roles.id"))

    user: Mapped["User"] = relationship(back_populates="membership")
    shop: Mapped["Shop"] = relationship(back_populates="memberships")
    role: Mapped["Role"] = relationship(back_populates="memberships")

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

    id: Mapped[UUID] = mapped_column(sa.UUID, primary_key=True)
    shop_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime.time] = mapped_column(sa.Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(sa.Time, nullable=False)
    label: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    shop: Mapped["Shop"] = relationship(back_populates="delivery_time_slots")

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
