from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.categories import Category
    from backend.infrastructure.persistence.tables.shops import Shop


class Product(Base, CreatedAt, UpdatedAt):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(sa.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=10, scale=2), nullable=False
    )

    category_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    shop_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE")
    )

    shop: Mapped["Shop"] = relationship(back_populates="products")
    category: Mapped["Category | None"] = relationship(
        back_populates="products"
    )

    def __repr__(self) -> str:
        return (
            f"<Product id={self.id}, name={self.name}, "
            f"price={self.price}, category_id={self.category_id}>"
        )
