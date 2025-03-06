from delivery_service.products_management.domain.errors import (
    ProductAlreadyExistsError,
)
from delivery_service.products_management.domain.product import Product


class ProductCollection(set[Product]):
    def add_product(self, new_product: Product) -> None:
        if new_product in self:
            raise ProductAlreadyExistsError()
        self.add(new_product)
