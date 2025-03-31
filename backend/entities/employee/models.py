from dataclasses import dataclass
from enum import StrEnum, auto
from typing import NewType

from entities.common.entity import BaseEntity
from entities.shop.models import ShopId
from entities.user.models import UserId

EmployeeId = NewType("EmployeeId", int)


class EmployeeRole(StrEnum):
    ADMIN = auto()
    MANAGER = auto()
    DRIVER = auto()


@dataclass(eq=False)
class Employee(BaseEntity[EmployeeId]):
    user_id: UserId
    shop_id: ShopId
    role: EmployeeRole
