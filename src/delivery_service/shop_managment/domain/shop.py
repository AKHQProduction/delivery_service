from datetime import date
from typing import NewType
from uuid import UUID

from delivery_service.identity.domain.user import User
from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.vo.location import Location
from delivery_service.shop_managment.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shop_managment.domain.value_objects import DaysOff

ShopID = NewType("ShopID", UUID)


class Shop(Entity[ShopID]):
    def __init__(
        self,
        entity_id: ShopID,
        *,
        name: str,
        location: Location,
        days_off: DaysOff,
        employees: EmployeeCollection,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._name = name
        self._location = location
        self._days_off = days_off
        self._employees = employees

    def edit_regular_days_off(self, days: list[int]) -> None:
        self._days_off = self._days_off.change_regular_days_off(days)

    def can_deliver_in_this_day(self, day: date) -> bool:
        return self._days_off.can_deliver_in_this_day(day)

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
    def employees(self) -> set[User]:
        return self._employees
