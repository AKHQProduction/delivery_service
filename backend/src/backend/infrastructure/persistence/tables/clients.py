from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    PhoneId,
    ShopId,
    TimeSlotId,
    UserId,
)
from backend.infrastructure.persistence.tables.base import (
    Base,
    CreatedAt,
    UpdatedAt,
)

if TYPE_CHECKING:
    from backend.infrastructure.persistence.tables.districts import District
    from backend.infrastructure.persistence.tables.orders import Order
    from backend.infrastructure.persistence.tables.shops import (
        Shop,
        ShopDeliveryTimeSlot,
    )
    from backend.infrastructure.persistence.tables.users import User


class Client(Base, CreatedAt, UpdatedAt):
    __tablename__ = "clients"

    id: Mapped[ClientId] = mapped_column(sa.UUID, primary_key=True)
    full_name: Mapped[str] = mapped_column(sa.String, nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=10, scale=2),
        nullable=False,
        default=Decimal(0),
        server_default=sa.text("0"),
    )

    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UserId | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    preferred_time_slot_id: Mapped[TimeSlotId | None] = mapped_column(
        sa.ForeignKey("shop_delivery_time_slots.id", ondelete="SET NULL"),
        nullable=True,
    )

    shop: Mapped["Shop"] = relationship(back_populates="clients", lazy="raise")
    user: Mapped["User"] = relationship(lazy="raise")
    preferred_time_slot: Mapped["ShopDeliveryTimeSlot | None"] = relationship(
        lazy="raise"
    )
    phones: Mapped[list["ClientPhone"]] = relationship(
        back_populates="client", cascade="all, delete-orphan", lazy="raise"
    )
    addresses: Mapped[list["ClientAddress"]] = relationship(
        back_populates="client", cascade="all, delete-orphan", lazy="raise"
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="client", cascade="all, delete-orphan", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} shop={self.shop_id}>"


class ClientPhone(Base, CreatedAt, UpdatedAt):
    __tablename__ = "client_phones"

    id: Mapped[PhoneId] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    number: Mapped[str] = mapped_column(sa.String, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )

    client_id: Mapped[ClientId] = mapped_column(
        sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[ShopId] = mapped_column(
        sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )

    client: Mapped["Client"] = relationship(
        back_populates="phones", lazy="raise"
    )
    shop: Mapped["Shop"] = relationship(lazy="raise")

    def __repr__(self) -> str:
        return (
            f"<ClientPhone id={self.id} number={self.number} "
            f"is_primary={self.is_primary}>"
        )


class ClientAddress(Base, CreatedAt, UpdatedAt):
    __tablename__ = "client_addresses"

    id: Mapped[AddressId] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )

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
    comment: Mapped[str | None] = mapped_column(
        sa.String, nullable=True, default=None
    )
    latitude: Mapped[float | None] = mapped_column(
        sa.Double, nullable=True, default=None
    )
    longitude: Mapped[float | None] = mapped_column(
        sa.Double, nullable=True, default=None
    )
    is_primary: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )

    client_id: Mapped[ClientId] = mapped_column(
        sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    district_id: Mapped[DistrictId | None] = mapped_column(
        sa.ForeignKey("districts.id", ondelete="SET NULL"), nullable=True
    )

    client: Mapped["Client"] = relationship(
        back_populates="addresses", lazy="raise"
    )
    district: Mapped["District | None"] = relationship(lazy="raise")

    __table_args__ = (
        sa.CheckConstraint(
            "(latitude IS NULL) = (longitude IS NULL)",
            name="ck_client_addresses_coords_both_or_none",
        ),
    )

    def __repr__(self) -> str:
        return f"<ClientAddress {self.street} {self.house}>"
