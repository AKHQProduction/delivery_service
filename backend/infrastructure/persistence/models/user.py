from enum import Enum

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.user import RoleName
from infrastructure.persistence.models.base import Base
from infrastructure.persistence.models.mixins import UpdatedAtMixin


class UserORM(Base, UpdatedAtMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
            sa.BigInteger, unique=True, primary_key=True, index=True
    )
    full_name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    username: Mapped[str] = mapped_column(
            sa.String(255), nullable=True, default=None, index=True
    )
    phone_number: Mapped[str] = mapped_column(
            sa.String(12), nullable=True, default=None
    )

    role: Mapped[RoleName] = mapped_column(
            sa.Enum(RoleName), default=RoleName.USER, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
            sa.Boolean, default=True, nullable=False
    )
