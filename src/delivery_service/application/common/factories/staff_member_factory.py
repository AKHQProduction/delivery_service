from typing import cast

from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.role_repository import RoleRepository
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import (
    Role,
    RoleCollection,
    StaffRole,
    StaffRoleID,
)


class StaffMemberFactory:
    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repository = role_repository

    async def create_staff_member(
        self, user_id: UserID, shop_id: ShopID, required_roles: list[Role]
    ) -> StaffMember:
        return StaffMember(
            entity_id=user_id,
            shop_id=shop_id,
            roles=RoleCollection(
                roles=await self._prepare_roles(required_roles)
            ),
        )

    async def _prepare_roles(
        self, required_roles: list[Role]
    ) -> list[StaffRole]:
        prepared_roles = []

        for role in required_roles:
            if exists_role := await self._role_repository.load_with_name(role):
                prepared_roles.append(exists_role)
            else:
                prepared_roles.append(
                    StaffRole(
                        entity_id=StaffRoleID(cast(int, None)), role_name=role
                    )
                )
        return prepared_roles
