from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from entities.employee.models import EmployeeRole
from entities.order.models import OrderStatus


@dataclass(frozen=True)
class EmployeeView:
    employee_id: int
    user_id: int
    full_name: str
    role: EmployeeRole


@dataclass(frozen=True)
class GoodsView:
    goods_id: UUID
    title: str
    price: Decimal


@dataclass(frozen=True)
class UserAddress:
    city: str | None
    street: str | None
    house_number: str | None

    @property
    def full_address(self) -> str | None:
        if any([self.city, self.street]):
            return f"{self.city}, {self.street} {self.house_number}"
        return None


@dataclass(frozen=True)
class UserView:
    user_id: int
    full_name: str
    username: str | None
    tg_id: int | None
    phone_number: str | None
    address: UserAddress


@dataclass(frozen=True)
class ShopView:
    title: str
    delivery_distance: int
    regular_days_off: list[int]
    special_days_off: list[datetime]


@dataclass(frozen=True)
class OrderItemView:
    title: str
    quantity: int


@dataclass(frozen=True)
class OrderView:
    status: OrderStatus
    total_price: Decimal
    items: list[OrderItemView]
