from delivery_service.identity.domain.user import User

# ruff: noqa: E501
from delivery_service.shared.infrastructure.integration.geopy.geolocator import (
    Geolocator,
)
from delivery_service.shop_managment.application.ports.id_generator import (
    ShopIDGenerator,
)
from delivery_service.shop_managment.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shop_managment.domain.factory import (
    DaysOffData,
    ShopFactory,
)
from delivery_service.shop_managment.domain.shop import Shop
from delivery_service.shop_managment.domain.value_objects import DaysOff


class ShopFactoryImpl(ShopFactory):
    def __init__(
        self, id_generator: ShopIDGenerator, geolocator: Geolocator
    ) -> None:
        self._id_generator = id_generator
        self._geolocator = geolocator

    async def create_shop(
        self,
        shop_name: str,
        shop_location: str,
        shop_days_off: DaysOffData,
        user: User,
    ) -> Shop:
        return Shop(
            entity_id=self._id_generator.generate_shop_id(),
            name=shop_name,
            location=await self._geolocator.get_location_data(shop_location),
            days_off=DaysOff(
                regular_days_off=shop_days_off.regular_days,
                irregular_days_off=shop_days_off.irregular_days,
            ),
            employees=EmployeeCollection(),
        )
