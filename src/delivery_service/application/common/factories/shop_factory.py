# ruff: noqa: E501
from dataclasses import dataclass, field
from datetime import date

from delivery_service.application.common.factories.staff_member_factory import (
    StaffMemberFactory,
)
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.shared.dto import CoordinatesData
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import (
    Coordinates,
)
from delivery_service.domain.shops.shop import Shop
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.domain.staff.staff_role import Role


@dataclass(frozen=True)
class DaysOffData:
    regular_days: list[int] = field(default_factory=list)
    irregular_days: list[date] = field(default_factory=list)


class ShopFactory:
    def __init__(
        self,
        id_generator: IDGenerator,
        staff_member_factory: StaffMemberFactory,
    ) -> None:
        self._id_generator = id_generator
        self._member_factory = staff_member_factory

    async def create_shop(
        self,
        shop_name: str,
        shop_coordinates: CoordinatesData,
        shop_days_off: DaysOffData,
        current_user_id: UserID,
    ) -> Shop:
        shop_id = self._id_generator.generate_shop_id()
        owner = await self._member_factory.create_staff_member(
            user_id=current_user_id,
            shop_id=shop_id,
            required_roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER, Role.COURIER],
        )

        return Shop(
            entity_id=shop_id,
            name=shop_name,
            coordinates=Coordinates(
                latitude=shop_coordinates.latitude,
                longitude=shop_coordinates.longitude,
            ),
            days_off=DaysOff(
                regular_days_off=shop_days_off.regular_days,
                irregular_days_off=shop_days_off.irregular_days,
            ),
            staff_members=[owner],
        )
