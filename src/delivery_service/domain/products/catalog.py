from delivery_service.domain.products.errors import AccessDeniedError
from delivery_service.domain.products.product import (
    Product,
    ProductID,
    ProductType,
)
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import Role


class ShopCatalog(Entity[ShopID]):
    def __init__(
        self, catalog_id: ShopID, *, staff_members: list[StaffMember]
    ) -> None:
        super().__init__(entity_id=catalog_id)

        self._staff_members = staff_members

    def add_new_product(
        self,
        product_id: ProductID,
        title: str,
        price: FixedDecimal,
        product_type: ProductType,
        creator_id: UserID,
    ) -> Product:
        self._check_shop_permission(creator_id)
        product_price = Price(value=price)

        new_product = Product(
            entity_id=product_id,
            title=title,
            price=product_price,
            product_type=product_type,
            shop_id=self.entity_id,
        )

        return new_product

    def _check_shop_permission(self, candidate_id: UserID) -> None:
        if not any(
            member.entity_id == candidate_id
            and any(
                role.name in [Role.SHOP_OWNER, Role.SHOP_MANAGER]
                for role in member.roles
            )
            for member in self._staff_members
        ):
            raise AccessDeniedError()
