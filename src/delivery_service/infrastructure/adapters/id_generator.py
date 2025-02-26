from uuid import UUID

from uuid_extensions import uuid7

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shops.shop import ShopID
from delivery_service.core.users.user import UserID


class IDGeneratorImpl(IDGenerator):
    def generate_user_id(self) -> UserID:
        return UserID(UUID(str(uuid7())))

    def generate_shop_id(self) -> ShopID:
        return ShopID(UUID(str(uuid7())))
