from delivery_service.identity.public.identity_id import UserID
from delivery_service.shared.domain.employee_collection import (
    EmployeeCollection,
)

# ruff: noqa: E501
from delivery_service.shared.infrastructure.integration.geopy.geolocator import (
    Geolocator,
)
from delivery_service.shop_management.application.ports.id_generator import (
    ShopIDGenerator,
)
from delivery_service.shop_management.domain.errors import (
    ShopCreationNotAllowedError,
)
from delivery_service.shop_management.domain.factory import (
    DaysOffData,
    ShopFactory,
)
from delivery_service.shop_management.domain.repository import (
    ShopRepository,
)
from delivery_service.shop_management.domain.shop import Shop
from delivery_service.shop_management.domain.value_objects import DaysOff


class ShopFactoryImpl(ShopFactory):
    def __init__(
        self,
        id_generator: ShopIDGenerator,
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
