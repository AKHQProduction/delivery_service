from uuid import UUID

from uuid_extensions import uuid7

from delivery_service.identity.application.ports.id_generator import (
    UserIDGenerator,
)
from delivery_service.identity.public.identity_id import UserID
from delivery_service.shared.domain.shop_id import ShopID
from delivery_service.shop_management.application.ports.id_generator import (
    ShopIDGenerator,
)


class IDGenerator(UserIDGenerator, ShopIDGenerator):
    def generate_user_id(self) -> UserID:
        return UserID(UUID(str(uuid7())))

    def generate_shop_id(self) -> ShopID:
        return ShopID(UUID(str(uuid7())))
