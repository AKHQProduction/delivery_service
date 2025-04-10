from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.products.errors import (
    AccessDeniedError,
    ProductAlreadyExistsError,
)
from delivery_service.domain.products.product import Product, ProductType
from delivery_service.domain.products.repository import ProductRepository
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import Role


class ProductFactory:
    def __init__(
        self, product_repository: ProductRepository, id_generator: IDGenerator
    ) -> None:
        self._product_repository = product_repository
        self._id_generator = id_generator

    async def create_new_product(
        self,
        title: str,
        price: FixedDecimal,
        product_type: ProductType,
        creator: StaffMember,
    ) -> Product:
        if not any(
            role.name in [Role.SHOP_OWNER, Role.SHOP_MANAGER]
            for role in creator.roles
        ):
            raise AccessDeniedError()
        if await self._product_repository.exists(title, creator.shop):
            raise ProductAlreadyExistsError()

        return Product(
            entity_id=self._id_generator.generate_product_id(),
            title=title,
            price=Price(price),
            product_type=product_type,
            shop_id=creator.shop,
        )
