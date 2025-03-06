from enum import Enum

from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shared.domain.tracker import Tracker


class EmployeeRole(Enum):
    SHOP_OWNER = "shop_owner"
    SHOP_MANAGER = "shop_manager"
    COURIER = "courier"


class Employee(Entity[UserID]):
    def __init__(
        self, employee_id: UserID, tracker: Tracker, *, role: EmployeeRole
    ) -> None:
        super().__init__(entity_id=employee_id, tracker=tracker)

        self._role = role
