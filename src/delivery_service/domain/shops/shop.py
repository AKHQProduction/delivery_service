from datetime import date
from typing import cast

from delivery_service.domain.orders.order import (
    DeliveryPreference,
    Order,
)
from delivery_service.domain.orders.order_ids import OrderID, OrderLineID
from delivery_service.domain.orders.order_line import OrderLine
from delivery_service.domain.shared.dto import OrderLineData
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import Coordinates
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.shared.vo.quantity import Quantity
from delivery_service.domain.shops.errors import (
    CantDeliveryInDaysOffError,
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

    def add_new_order(
        self,
        new_order_id: OrderID,
        order_line_data: list[OrderLineData],
        customer_id: UserID,
        coordinates: Coordinates,
        delivery_preference: DeliveryPreference,
        delivery_date: date,
        creator_id: UserID,
    ) -> Order:
        self._member_with_admin_roles(candidate_id=creator_id)
        self._can_deliver_in_this_day(delivery_date)

        order_lines = [
            OrderLine(
                entity_id=OrderLineID(cast(int, None)),
                product_id=data.product_id,
                order_id=new_order_id,
                title=data.title,
                price_per_item=Price(data.price_per_item),
                quantity=Quantity(data.quantity),
            )
            for data in order_line_data
        ]

        return Order(
            entity_id=new_order_id,
            shop_id=self.id,
            customer_id=customer_id,
            coordinates=coordinates,
            order_lines=order_lines,
            delivery_preference=delivery_preference,
            delivery_date=delivery_date,
        )

    def can_delete_order(
        self, order_shop_id: ShopID, deleter_id: UserID
    ) -> None:
        self._is_current_shop_order(order_shop_id)
        self._member_with_admin_roles(deleter_id)

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

    def edit_regular_days_off(self, days: list[int]) -> None:
        self._days_off = self._days_off.change_regular_days_off(days)

    def _can_deliver_in_this_day(self, day: date) -> None:
        if not self._days_off.can_deliver_in_this_day(day):
            raise CantDeliveryInDaysOffError()

    def _member_with_admin_roles(self, candidate_id: UserID) -> None:
        self._check_roles(
            required_roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER],
            candidate_id=candidate_id,
        )

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

    def _is_current_shop_order(self, order_shop_id: ShopID) -> None:
        if not (order_shop_id == self.id):
            raise AccessDeniedError()

    @property
    def id(self) -> ShopID:
        return self.entity_id

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
