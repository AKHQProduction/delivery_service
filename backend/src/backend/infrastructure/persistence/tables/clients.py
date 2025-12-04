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
    from backend.infrastructure.persistence.tables.shops import Shop
    from backend.infrastructure.persistence.tables.users import User


class Client(Base, CreatedAt, UpdatedAt):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True)
    full_name: Mapped[str] = mapped_column(sa.String, nullable=False)

    shop_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    shop: Mapped["Shop"] = relationship(back_populates="clients")
    user: Mapped["User"] = relationship()
    phones: Mapped[list["ClientPhone"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
    addresses: Mapped[list["ClientAddress"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} shop={self.shop_id}>"


class ClientPhone(Base, CreatedAt, UpdatedAt):
    __tablename__ = "client_phones"

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    number: Mapped[str] = mapped_column(sa.String, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )

    client: Mapped["Client"] = relationship(back_populates="phones")
    shop: Mapped["Shop"] = relationship()

    __table_args__ = (
        sa.UniqueConstraint(
            "shop_id", "number", name="uq_client_phone_per_shop"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ClientPhone id={self.id} number={self.number} "
            f"is_primary={self.is_primary}>"
        )


class ClientAddress(Base, CreatedAt, UpdatedAt):
    __tablename__ = "client_addresses"

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )

    address_type: Mapped[str] = mapped_column(sa.String, nullable=False)
    street: Mapped[str] = mapped_column(sa.String, nullable=False)
    house: Mapped[str] = mapped_column(sa.String, nullable=False)

    apartment: Mapped[str | None] = mapped_column(
        sa.String, nullable=True, default=None
    )
    entrance: Mapped[str | None] = mapped_column(
        sa.String, nullable=True, default=None, comment="Подъезд"
    )
    floor: Mapped[str | None] = mapped_column(
        sa.String, nullable=True, default=None
    )
    intercom: Mapped[str | None] = mapped_column(
        sa.String, nullable=True, default=None
    )
    is_primary: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )

    client: Mapped["Client"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return (
            f"<ShopClientAddress address_type={self.address_type} "
            f"{self.street} {self.house}>"
        )
