from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shops.errors import ShopCreationNotAllowedError
from delivery_service.core.shops.factory import DaysOffData, ShopFactory
from delivery_service.core.shops.shop import Shop
from delivery_service.core.shops.value_objects import DaysOff
from delivery_service.core.users.user import User, UserRole
from delivery_service.infrastructure.integration.geopy.geolocator import (
    Geolocator,
)


class ShopFactoryImpl(ShopFactory):
    def __init__(
        self, id_generator: IDGenerator, geolocator: Geolocator
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
        if user.role != UserRole.USER:
            raise ShopCreationNotAllowedError(user_id=user.entity_id)

        return Shop(
            entity_id=self._id_generator.generate_shop_id(),
            name=shop_name,
            location=await self._geolocator.get_location_data(shop_location),
            days_off=DaysOff(
                regular_days_off=shop_days_off.regular_days,
                irregular_days_off=shop_days_off.irregular_days,
            ),
        )
