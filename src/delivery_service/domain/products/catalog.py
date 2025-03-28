from decimal import Decimal

from delivery_service.domain.products.product import (
    Product,
    ProductID,
    ProductType,
)
from delivery_service.domain.products.product_collection import (
    ProductCollection,
)
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.price import Price


class ShopCatalog(Entity[ShopID]):
    def __init__(
        self,
        catalog_id: ShopID,
        *,
        products: ProductCollection,
    ) -> None:
        super().__init__(entity_id=catalog_id)

        self._products = products

    def add_new_product(
        self,
        product_id: ProductID,
        title: str,
        product_price: Decimal,
        product_type: ProductType,
    ) -> Product:
        price = Price(value=product_price)
        new_product = Product(
            product_id=product_id,
            title=title,
            price=price,
            product_type=product_type,
            shop_id=self.entity_id,
        )
        self._products.add_product(new_product)

        return new_product
