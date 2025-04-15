from datetime import date

from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.phone_number import (
    PhoneBook,
    PhoneNumber,
)
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import Coordinates
from delivery_service.domain.shops.errors import (
    CantDiscardYourselfError,
    UserAlreadyInStaffError,
    UserNotFoundInShopStaffError,
)
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import Role, RoleCollection


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

    def add_staff_member(
        self,
        new_staff_id: UserID,
        required_roles: RoleCollection,
        hirer_id: UserID,
    ) -> None:
        self._check_roles(
            required_roles=[Role.SHOP_OWNER], candidate_id=hirer_id
        )

        self._add_staff_member(new_staff_id, required_roles)

    def join_to_staff_members(
        self, candidate_id: UserID, required_roles: RoleCollection
    ) -> None:
        self._add_staff_member(candidate_id, required_roles)

    def discard_staff_member(
        self, staff_member_id: UserID, firer_id: UserID
    ) -> None:
        if staff_member_id == firer_id:
            raise CantDiscardYourselfError()
        self._check_roles(
            required_roles=[Role.SHOP_OWNER], candidate_id=firer_id
        )

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

    def add_new_customer(
        self,
        customer_id: UserID,
        customer_full_name: str,
        primary_phone_number: str,
    ) -> Customer:
        return Customer(
            entity_id=customer_id,
            shop_id=self.entity_id,
            full_name=customer_full_name,
            contacts=PhoneBook(primary=PhoneNumber(primary_phone_number)),
            delivery_address=None,
        )

    def edit_regular_days_off(self, days: list[int]) -> None:
        self._days_off = self._days_off.change_regular_days_off(days)

    def can_deliver_in_this_day(self, day: date) -> bool:
        return self._days_off.can_deliver_in_this_day(day)

    def _check_roles(
        self, required_roles: list[Role], candidate_id: UserID
    ) -> None:
        current_staff_member = next(
            (
                member
                for member in self._staff_members
                if member.entity_id == candidate_id
            ),
            None,
        )
        if not current_staff_member:
            raise AccessDeniedError()
        if not any(
            current_staff_member.has_role(role) for role in required_roles
        ):
            raise AccessDeniedError()

    def _add_staff_member(
        self, candidate_id: UserID, roles: RoleCollection
    ) -> None:
        staff_member = next(
            (
                member
                for member in self._staff_members
                if member.entity_id == candidate_id
            ),
            None,
        )
        if not staff_member:
            self._staff_members.append(
                StaffMember(
                    entity_id=candidate_id, roles=roles, shop_id=self.entity_id
                )
            )
        raise UserAlreadyInStaffError(candidate_id)

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
