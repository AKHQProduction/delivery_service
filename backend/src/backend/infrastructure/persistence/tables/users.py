import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, UpdatedAt

if TYPE_CHECKING:
    from .shops import ShopMembership


class User(Base, CreatedAt, UpdatedAt):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True)

    telegram_account: Mapped["TelegramAccount"] = relationship(
        back_populates="user", uselist=False
    )
    membership: Mapped["ShopMembership | None"] = relationship(
        back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id}>"


class TelegramAccount(Base, CreatedAt, UpdatedAt):
    __tablename__ = "telegram_accounts"

    id: Mapped[int] = mapped_column(
        sa.BIGINT, primary_key=True, autoincrement=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    telegram_id: Mapped[int] = mapped_column(
        sa.BigInteger, nullable=False, unique=True
    )
    full_name: Mapped[str] = mapped_column(sa.String, nullable=False)

    user: Mapped["User"] = relationship(back_populates="telegram_account")

    def __repr__(self) -> str:
        return (
            f"<TelegramAccount tg_id={self.telegram_id} "
            f"full_name={self.full_name}>"
        )
