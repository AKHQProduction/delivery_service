from datetime import date

from delivery_service.identity.public.identity_id import UserID
from delivery_service.shared.domain.employee import (
    Employee,
    EmployeeRole,
)
from delivery_service.shared.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.shop_id import ShopID
from delivery_service.shared.domain.vo.location import Location
from delivery_service.shop_management.domain.errors import NotOwnerError
from delivery_service.shop_management.domain.value_objects import DaysOff


class Shop(Entity[ShopID]):
    def __init__(
        self,
        entity_id: ShopID,
        *,
        owner_id: UserID,
        name: str,
        location: Location,
        days_off: DaysOff,
        employees: EmployeeCollection,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._owner_id = owner_id
        self._name = name
        self._location = location
        self._days_off = days_off
        self._employees = employees

    def add_employee(
        self, employee_id: UserID, role: EmployeeRole, hirer_id: UserID
    ) -> Employee:
        self._ensure_is_owner(hirer_id)

        employee = Employee(employee_id=employee_id, role=role)
        self._employees.add_to_employees(employee)

        return employee

    def discard_employee(self, employee: Employee, firer_id: UserID) -> None:
        self._ensure_is_owner(firer_id)
        self._employees.discard_from_employees(employee)

    def edit_regular_days_off(self, days: list[int]) -> None:
        self._days_off = self._days_off.change_regular_days_off(days)

    def can_deliver_in_this_day(self, day: date) -> bool:
        return self._days_off.can_deliver_in_this_day(day)

    def _ensure_is_owner(self, candidate_id: UserID) -> None:
        if candidate_id != self._owner_id:
            raise NotOwnerError()

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> str:
        return self._location.full_address

    @property
    def location_coordinates(self) -> tuple[float, float]:
        return self._location.latitude, self._location.longitude

    @property
    def regular_days_off(self) -> list[int]:
        return self._days_off.regular_days_off

    @property
    def irregular_days_off(self) -> list[date]:
        return self._days_off.irregular_days_off

    @property
    def employees(self) -> set[Employee]:
        return self._employees
