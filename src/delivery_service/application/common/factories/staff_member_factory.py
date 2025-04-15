from delivery_service.application.common.factories.role_factory import (
    RoleFactory,
)
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import (
    Role,
)


class StaffMemberFactory:
    def __init__(self, role_factory: RoleFactory) -> None:
        self._role_factory = role_factory

    async def create_staff_member(
        self, user_id: UserID, shop_id: ShopID, required_roles: list[Role]
    ) -> StaffMember:
        return StaffMember(
            entity_id=user_id,
            shop_id=shop_id,
            roles=await self._role_factory.restore_roles(
                required_roles=required_roles
            ),
        )
