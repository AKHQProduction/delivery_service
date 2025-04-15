from delivery_service.domain.products.product import (
    Product,
    ProductID,
    ProductType,
)
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import Role


class ShopCatalog(Entity[ShopID]):
    def __init__(
        self, entity_id: ShopID, *, staff_members: list[StaffMember]
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._staff_members = staff_members

    def add_product(
        self,
        new_product_id: ProductID,
        title: str,
        price: FixedDecimal,
        product_type: ProductType,
        creator_id: UserID,
    ) -> Product:
        self._member_with_admin_roles(candidate_id=creator_id)

        return Product(
            entity_id=new_product_id,
            shop_id=self.entity_id,
            title=title,
            price=Price(price),
            product_type=product_type,
        )

    def delete_product(self, product: Product, deleter_id: UserID) -> None:
        self._member_with_admin_roles(deleter_id)
        self._is_current_shop_product(product.from_shop)

    def edit_product_title(
        self, new_title: str, product: Product, editor_id: UserID
    ) -> None:
        self._member_with_admin_roles(editor_id)
        self._is_current_shop_product(product.from_shop)

        product.edit_title(new_title)

    def edit_product_price(
        self, new_price: FixedDecimal, product: Product, editor_id: UserID
    ) -> None:
        self._member_with_admin_roles(editor_id)
        self._is_current_shop_product(product.from_shop)

        product.edit_price(new_price)

    def _check_roles(
        self, required_roles: list[Role], candidate_id: UserID
    ) -> None:
        current_staff_member = next(
            (
                member
                for member in self._staff_members
                if member.entity_id == candidate_id
            ),
            None,
        )
        if not current_staff_member:
            raise AccessDeniedError()
        if not any(
            current_staff_member.has_role(role) for role in required_roles
        ):
            raise AccessDeniedError()

    def _member_with_admin_roles(self, candidate_id: UserID) -> None:
        self._check_roles(
            required_roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER],
            candidate_id=candidate_id,
        )

    def _is_current_shop_product(self, product_shop_id: ShopID) -> None:
        if not (product_shop_id == self.id):
            raise AccessDeniedError()

    @property
    def id(self) -> ShopID:
        return self.entity_id
