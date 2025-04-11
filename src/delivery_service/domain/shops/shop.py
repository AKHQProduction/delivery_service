from datetime import date

from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.location import Coordinates
from delivery_service.domain.shops.errors import (
    CantDiscardYourselfError,
    UserAlreadyInStaffError,
    UserNotFoundInShopStaffError,
)
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.domain.staff.staff_member import StaffMember


class Shop(Entity[ShopID]):
    def __init__(
        self,
        entity_id: ShopID,
        *,
        name: str,
        coordinates: Coordinates,
        days_off: DaysOff,
        staff_members: list[StaffMember] | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._name = name
        self._coordinates = coordinates
        self._days_off = days_off
        self._staff_members = staff_members or []

    def add_staff_member(self, new_staff_member: StaffMember) -> None:
        if new_staff_member in self._staff_members:
            raise UserAlreadyInStaffError(new_staff_member.entity_id)

        self._staff_members.append(new_staff_member)

    def discard_staff_member(
        self, staff_member_id: UserID, firer_id: UserID
    ) -> None:
        if staff_member_id == firer_id:
            raise CantDiscardYourselfError()

        staff_member = next(
            (
                member
                for member in self._staff_members
                if member.entity_id == staff_member_id
            ),
            None,
        )
        if not staff_member:
            raise UserNotFoundInShopStaffError(staff_member_id)

        self._staff_members.remove(staff_member)

    def edit_regular_days_off(self, days: list[int]) -> None:
        self._days_off = self._days_off.change_regular_days_off(days)

    def can_deliver_in_this_day(self, day: date) -> bool:
        return self._days_off.can_deliver_in_this_day(day)

    @property
    def name(self) -> str:
        return self._name

    @property
    def shop_coordinates(self) -> tuple[float, float]:
        return self._coordinates.coordinates

    @property
    def regular_days_off(self) -> list[int]:
        return self._days_off.regular_days_off

    @property
    def irregular_days_off(self) -> list[date]:
        return self._days_off.irregular_days_off

    @property
    def staff_members(self) -> list[StaffMember]:
        return self._staff_members
