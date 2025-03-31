# ruff: noqa: E501
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.employee_collection import (
    EmployeeCollection,
)
from delivery_service.domain.shops.errors import (
    ShopCreationNotAllowedError,
)
from delivery_service.domain.shops.factory import (
    DaysOffData,
    ShopFactory,
)
from delivery_service.domain.shops.repository import (
    ShopRepository,
)
from delivery_service.domain.shops.shop import Shop
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.infrastructure.integration.geopy.geolocator import (
    Geolocator,
)


class ShopFactoryImpl(ShopFactory):
    def __init__(
        self,
        id_generator: IDGenerator,
        geolocator: Geolocator,
        shop_repository: ShopRepository,
    ) -> None:
        self._id_generator = id_generator
        self._geolocator = geolocator
        self._shop_repository = shop_repository

    async def create_shop(
        self,
        shop_name: str,
        shop_location: str,
        shop_days_off: DaysOffData,
        identity_id: UserID,
    ) -> Shop:
        if await self._shop_repository.exists(identity_id):
            raise ShopCreationNotAllowedError(identity_id)

        return Shop(
            entity_id=self._id_generator.generate_shop_id(),
            owner_id=identity_id,
            name=shop_name,
            location=await self._geolocator.get_location_data(shop_location),
            days_off=DaysOff(
                regular_days_off=shop_days_off.regular_days,
                irregular_days_off=shop_days_off.irregular_days,
            ),
            employees=EmployeeCollection(),
        )
