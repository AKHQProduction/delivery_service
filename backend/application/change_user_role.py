import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.gateways.user import UserReader, UserSaver
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.errors.access import AccessDeniedError
from application.errors.user import RoleAlreadyAssignedError
from application.specs.has_role import HasRoleSpec
from application.common.specification import Specification
from domain.entities.user import RoleName
from domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class ChangeUserRoleDTO:
    user_id: int
    role: RoleName


class ChangeUserRole(Interactor[ChangeUserRoleDTO, None]):
    def __init__(
            self,
            user_reader: UserReader,
            user_saver: UserSaver,
            commiter: Commiter,
            id_provider: IdentityProvider,
    ):
        self._user_reader = user_reader
        self._user_saver = user_saver
        self._commiter = commiter
        self._id_provider = id_provider

    async def __call__(self, data: ChangeUserRoleDTO) -> None:
        actor_role = await self._id_provider.get_user_role()
        rule: Specification = HasRoleSpec(RoleName.ADMIN)

        if not rule.is_satisfied_by(actor_role):
            logging.info("Access denied to user with role %s", actor_role)
            raise AccessDeniedError()

        user = await self._user_reader.by_id(UserId(data.user_id))

        if data.role == user.role:
            logging.info("Attempting to change an already assigned role")
            raise RoleAlreadyAssignedError()

        user.change_role(data.role)

        await self._user_saver.update(user)
        await self._commiter.commit()

        logging.info(
                f"User {user.user_id.to_raw()} role "
                f"successfully update to {data.role}"
        )
