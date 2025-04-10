from delivery_service.domain.products.product import Product
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import Role, RoleCollection


class ProductAccessService:
    def can_create_product(self, member: StaffMember) -> None:
        self._check_roles(
            roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER],
            member_roles=member.roles,
        )

    def can_edit_product(self, member: StaffMember, product: Product) -> None:
        self._is_same_shop(member.from_shop, product.from_shop)
        self._check_roles(
            roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER],
            member_roles=member.roles,
        )

    def can_delete_product(
        self, member: StaffMember, product: Product
    ) -> None:
        self._is_same_shop(member.from_shop, product.from_shop)
        self._check_roles(
            roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER],
            member_roles=member.roles,
        )

    @staticmethod
    def _is_same_shop(member_shop_id: ShopID, product_shop_id: ShopID) -> None:
        if member_shop_id != product_shop_id:
            raise AccessDeniedError()

    @staticmethod
    def _check_roles(roles: list[Role], member_roles: RoleCollection) -> None:
        if not any(role.name in roles for role in member_roles):
            raise AccessDeniedError()
