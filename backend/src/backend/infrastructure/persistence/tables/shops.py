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
    from backend.infrastructure.persistence.tables.product import Product
    from backend.infrastructure.persistence.tables.users import User


class Shop(Base, CreatedAt, UpdatedAt):
    __tablename__ = "shops"

    id: Mapped[UUID] = mapped_column(sa.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    memberships: Mapped[list["ShopMembership"]] = relationship(
        back_populates="shop"
    )
    products: Mapped[list["Product"]] = relationship(back_populates="shop")

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
