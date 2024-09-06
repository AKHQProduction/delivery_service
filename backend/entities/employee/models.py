from dataclasses import dataclass
from enum import StrEnum, auto
from typing import NewType

from entities.shop.models import ShopId
from entities.user.models import UserId

EmployeeId = NewType("EmployeeId", int)


class EmployeeRole(StrEnum):
    ADMIN = auto()
    MANAGER = auto()
    DRIVER = auto()


@dataclass
class Employee:
    employee_id: EmployeeId
    user_id: UserId
    shop_id: ShopId
    role: EmployeeRole
