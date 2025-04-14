from dataclasses import dataclass, field
from datetime import date

from delivery_service.application.ports.location_finder import LocationFinder
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.address import Coordinates
from delivery_service.domain.shops.shop import Shop
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.domain.staff.staff_member import StaffMember


@dataclass(frozen=True)
class DaysOffData:
    regular_days: list[int] = field(default_factory=list)
    irregular_days: list[date] = field(default_factory=list)


@dataclass(frozen=True)
class CoordinatesData:
    latitude: float
    longitude: float


class ShopFactory:
    def __init__(self, location_finder: LocationFinder) -> None:
        self._location_finder = location_finder

    def create_shop(
        self,
        shop_id: ShopID,
        shop_name: str,
        shop_coordinates: CoordinatesData,
        shop_days_off: DaysOffData,
        owner: StaffMember,
    ) -> Shop:
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
