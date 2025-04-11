from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.staff.staff_role import Role, RoleCollection


class ShopAccessService:
    def can_add_staff_member(self, current_user_roles: RoleCollection) -> None:
        self._check_roles([Role.SHOP_OWNER], current_user_roles)

    def can_remove_staff_member(
        self, current_user_roles: RoleCollection
    ) -> None:
        self._check_roles([Role.SHOP_OWNER], current_user_roles)

    @staticmethod
    def _check_roles(roles: list[Role], member_roles: RoleCollection) -> None:
        if not any(role.name in roles for role in member_roles):
            raise AccessDeniedError()
