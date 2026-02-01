from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.application.vars import CategoryId, ShopId
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.products import Product
    from backend.infrastructure.persistence.tables.shops import Shop


class Category(Base, CreatedAt, UpdatedAt):
    __tablename__ = "categories"

    id: Mapped[CategoryId] = mapped_column(sa.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE")
    )

    shop: Mapped["Shop"] = relationship(back_populates="categories")
    products: Mapped[list["Product"]] = relationship(back_populates="category")

    __table_args__ = (
        UniqueConstraint("shop_id", "name", name="uq_category_name_per_shop"),
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id}, name={self.name}>"
