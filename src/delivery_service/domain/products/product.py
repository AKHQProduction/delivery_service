from enum import Enum
from typing import NewType
from uuid import UUID

from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.price import Price

ProductID = NewType("ProductID", UUID)


class ProductType(Enum):
    WATER = "water"
    ACCESSORIES = "accessories"


class Product(Entity[ProductID]):
    def __init__(
        self,
        entity_id: ProductID,
        *,
        shop_id: ShopID,
        title: str,
        price: Price,
        product_type: ProductType,
        metadata_path: str | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._shop_id = shop_id

        self._title = title
        self._price = price
        self._product_type = product_type
        self._metadata_path = metadata_path

    @property
    def title(self) -> str:
        return self._title

    @property
    def cost(self) -> Price:
        return self._price

    @property
    def product_type(self) -> ProductType:
        return self._product_type

    @property
    def metadata_path(self) -> str | None:
        return self._metadata_path

    @property
    def from_shop(self) -> ShopID:
        return self._shop_id
