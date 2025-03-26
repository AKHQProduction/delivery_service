from decimal import Decimal

from delivery_service.identity.public.identity_id import UserID
from delivery_service.products_management.domain.errors import (
    AccessDeniedError,
)
from delivery_service.products_management.domain.product import (
    Product,
    ProductID,
    ProductType,
)
from delivery_service.products_management.domain.product_collection import (
    ProductCollection,
)
from delivery_service.shared.domain.employee import EmployeeRole
from delivery_service.shared.domain.employee_collection import (
    EmployeeCollection,
)
from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.shop_id import ShopID
from delivery_service.shared.domain.vo.price import Price


class ShopCatalog(Entity[ShopID]):
    def __init__(
        self,
        catalog_id: ShopID,
        *,
        employees: EmployeeCollection,
        products: ProductCollection,
    ) -> None:
        super().__init__(entity_id=catalog_id)

        self._employees = employees
        self._products = products

    def add_new_product(
        self,
        product_id: ProductID,
        title: str,
        product_price: Decimal,
        product_type: ProductType,
        creator_id: UserID,
    ) -> Product:
        self._ensure_user_in_administration(creator_id)

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

    def _ensure_user_in_administration(self, candidate_id: UserID) -> None:
        employee = self._employees.get(employee_id=candidate_id)
        if employee.role not in [
            EmployeeRole.SHOP_MANAGER,
            EmployeeRole.SHOP_OWNER,
        ]:
            raise AccessDeniedError()
