from dataclasses import dataclass, field
from datetime import date

from delivery_service.application.ports.location_finder import LocationFinder
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.location import Location
from delivery_service.domain.shops.shop import Shop
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.domain.staff.staff_member import StaffMember


@dataclass(frozen=True)
class DaysOffData:
    regular_days: list[int] = field(default_factory=list)
    irregular_days: list[date] = field(default_factory=list)


class ShopFactory:
    def __init__(self, location_finder: LocationFinder) -> None:
        self._location_finder = location_finder

    async def create_shop(
        self,
        shop_id: ShopID,
        shop_name: str,
        shop_location: str,
        shop_days_off: DaysOffData,
        owner: StaffMember,
    ) -> Shop:
        location_data = await self._location_finder.find_location(
            shop_location
        )

        return Shop(
            entity_id=shop_id,
            name=shop_name,
            location=Location(
                city=location_data.city,
                street=location_data.street,
                house_number=location_data.house_number,
                latitude=location_data.latitude,
                longitude=location_data.longitude,
            ),
            days_off=DaysOff(
                regular_days_off=shop_days_off.regular_days,
                irregular_days_off=shop_days_off.irregular_days,
            ),
            staff_members=[owner],
        )
