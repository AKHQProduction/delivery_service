from enum import Enum

from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.identity_id import UserID


class EmployeeRole(Enum):
    SHOP_OWNER = "shop_owner"
    SHOP_MANAGER = "shop_manager"
    COURIER = "courier"


class Employee(Entity[UserID]):
    def __init__(self, employee_id: UserID, *, role: EmployeeRole) -> None:
        super().__init__(entity_id=employee_id)

        self._role = role

    @property
    def role(self) -> EmployeeRole:
        return self._role
