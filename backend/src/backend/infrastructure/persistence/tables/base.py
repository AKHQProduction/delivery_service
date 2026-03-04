from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from backend.application.dto.coordinates import CoordinatesDTO


@dataclass
class DeliveryAddressDTO(Mutable):
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None
    district: str | None = None
    coordinates: CoordinatesDTO | None = None

    @classmethod
    def coerce(  # type: ignore[override]
        cls,
        key: str,
        value: Any,
    ) -> "DeliveryAddressDTO | None":
        if isinstance(value, cls):
            return value
        return super().coerce(key, value)

    def __setattr__(  # type: ignore[override]
        self,
        key: str,
        value: Any,
    ) -> None:
        object.__setattr__(self, key, value)
        self.changed()


class DeliveryAddressType(TypeDecorator):
    impl = JSONB
    cache_ok = True

    def process_bind_param(
        self, value: DeliveryAddressDTO | dict | None, dialect: Any
    ) -> dict | None:
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        return asdict(value)

    def process_result_value(
        self, value: dict | None, dialect: Any
    ) -> DeliveryAddressDTO | None:
        if value is None:
            return None
        coords = value.pop("coordinates", None)
        if coords is not None:
            coords = CoordinatesDTO(**coords)
        return DeliveryAddressDTO(**value, coordinates=coords)


class Base(DeclarativeBase):
    pass


class CreatedAt:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )


class UpdatedAt:
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
