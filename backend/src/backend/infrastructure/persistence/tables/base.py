from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CreatedAt:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )


class UpdatedAt:
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
