import logging
from dataclasses import dataclass

from application.common.gateways.user import UserReader
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.common.dto import UserDTO
from application.errors.access import AccessDeniedError
from application.errors.user import UserIsNotExistError
from application.specs.has_role import HasRoleSpec
from domain.entities.user import RoleName
from domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class GetUserInputDTO:
    user_id: int


class GetUser(Interactor[GetUserInputDTO, UserDTO]):
    def __init__(
            self,
            user_reader: UserReader,
            id_provider: IdentityProvider
    ):
        self._user_reader = user_reader
        self._id_provider = id_provider

    async def __call__(self, data: GetUserInputDTO) -> UserDTO:
        actor_role = await self._id_provider.get_user_role()

        rule: Specification = (
                HasRoleSpec(RoleName.ADMIN) or HasRoleSpec(RoleName.MANAGER)
        )

        if not rule.is_satisfied_by(actor_role):
            logging.info(
                    "GetUser: access denied to user with role %s",
                    actor_role
            )
            raise AccessDeniedError()

        user_id = UserId(data.user_id)

        user = await self._user_reader.by_id(user_id)

        if user is None:
            logging.info(
                    "GetUser: user with id %s not found",
                    user_id.to_raw()
            )
            raise UserIsNotExistError(user_id.to_raw())

        logging.info(
                "GetUser: successfully get user %s",
                user_id.to_raw()
        )

        return UserDTO(
                user_id=user_id.to_raw(),
                full_name=user.full_name,
                username=user.username,
                phone_number=user.phone_number
        )
