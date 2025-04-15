from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shop_catalogs.shop_catalog import ShopCatalog


class ShopCatalogRepository(Protocol):
    @abstractmethod
    async def load_with_id(self, shop_id: ShopID) -> ShopCatalog | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_identity(
        self, identity_id: UserID
    ) -> ShopCatalog | None:
        raise NotImplementedError
