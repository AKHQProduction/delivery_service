from uuid import UUID

from uuid_extensions import uuid7

from delivery_service.identity.application.ports.id_generator import (
    UserIDGenerator,
)
from delivery_service.identity.domain.user import UserID
from delivery_service.shop_managment.application.ports.id_generator import (
    ShopIDGenerator,
)
from delivery_service.shop_managment.domain.shop import ShopID


class IDGenerator(UserIDGenerator, ShopIDGenerator):
    def generate_user_id(self) -> UserID:
        return UserID(UUID(str(uuid7())))

    def generate_shop_id(self) -> ShopID:
        return ShopID(UUID(str(uuid7())))
