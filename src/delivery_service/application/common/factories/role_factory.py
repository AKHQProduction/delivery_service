from typing import cast

from delivery_service.domain.staff.role_repository import RoleRepository
from delivery_service.domain.staff.staff_role import (
    Role,
    RoleCollection,
    StaffRole,
    StaffRoleID,
)


class RoleFactory:
    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repository = role_repository

    async def restore_roles(
        self, required_roles: list[Role]
    ) -> RoleCollection:
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
        return RoleCollection(roles=prepared_roles)
