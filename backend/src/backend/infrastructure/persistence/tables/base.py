from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from backend.application.interfaces.gateways.order_gateway import (
    DeliveryAddressDTO,
)


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
        return DeliveryAddressDTO(**value)


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
