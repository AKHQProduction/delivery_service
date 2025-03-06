from datetime import date
from typing import NewType
from uuid import UUID

from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shared.domain.tracker import Tracker
from delivery_service.shared.domain.vo.location import Location
from delivery_service.shop_managment.domain.employee import (
    Employee,
    EmployeeRole,
)
from delivery_service.shop_managment.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shop_managment.domain.errors import NotOwnerError
from delivery_service.shop_managment.domain.value_objects import DaysOff

ShopID = NewType("ShopID", UUID)


class Shop(Entity[ShopID]):
    def __init__(
        self,
        entity_id: ShopID,
        tracker: Tracker,
        *,
        owner_id: UserID,
        name: str,
        location: Location,
        days_off: DaysOff,
        employees: EmployeeCollection,
    ) -> None:
        super().__init__(entity_id=entity_id, tracker=tracker)

        self._owner_id = owner_id
        self._name = name
        self._location = location
        self._days_off = days_off
        self._employees = employees

    def add_employee(
        self, employee_id: UserID, role: EmployeeRole, hirer: UserID
    ) -> None:
        self._ensure_is_owner(hirer)

        employee = Employee(
            employee_id=employee_id, tracker=self._tracker, role=role
        )
        self._employees.add_employee(employee)
        self._tracker.add_new(employee)

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
