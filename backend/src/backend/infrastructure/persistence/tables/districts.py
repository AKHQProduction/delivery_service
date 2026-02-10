from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.application.vars import DistrictId, ShopId
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.shops import Shop


class District(Base, CreatedAt, UpdatedAt):
    __tablename__ = "districts"

    id: Mapped[DistrictId] = mapped_column(sa.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE")
    )

    shop: Mapped["Shop"] = relationship(
        back_populates="districts", lazy="raise"
    )

    __table_args__ = (
        UniqueConstraint("shop_id", "name", name="uq_district_name_per_shop"),
    )

    def __repr__(self) -> str:
        return f"<District id={self.id}, name={self.name}>"
