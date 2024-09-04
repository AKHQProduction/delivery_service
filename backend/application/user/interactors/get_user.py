import logging
from dataclasses import dataclass

from application.user.gateways.user import UserReader
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.user.dto.user import UserDTO
from application.errors.access import AccessDeniedError
from application.user.errors.user import UserIsNotExistError
from application.specs.has_role import HasRoleSpec
from domain.user.entity.user import RoleName, UserId


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
        actor = await self._id_provider.get_user()

        rule: Specification = (
                HasRoleSpec(RoleName.ADMIN) or HasRoleSpec(RoleName.MANAGER)
        )

        if not rule.is_satisfied_by(actor.role):
            logging.info(
                    "GetUser: access denied to user with role %s",
                    actor.role
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
