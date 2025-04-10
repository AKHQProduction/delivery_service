from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from delivery_service.domain.products.product import ProductID, ProductType
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.shop_id import ShopID


@dataclass(frozen=True)
class ProductReadModel:
    product_id: ProductID
    title: str
    price: FixedDecimal
    product_type: ProductType


@dataclass(frozen=True)
class ProductGatewayFilters:
    shop_id: ShopID | None = None


class ProductGateway(Protocol):
    @abstractmethod
    async def read_with_id(
        self, product_id: ProductID
    ) -> ProductReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all_products(
        self, filters: ProductGatewayFilters | None = None
    ) -> Sequence[ProductReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: ProductGatewayFilters | None = None) -> int:
        raise NotImplementedError
