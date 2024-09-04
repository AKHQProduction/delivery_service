import logging
from dataclasses import dataclass

from application.user.gateway import UserReader
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.errors.access import AccessDeniedError
from application.user.errors import UserIsNotExistError
from application.specs.has_role import HasRoleSpec
from entities.user.model import RoleName, UserId


@dataclass(frozen=True)
class GetUserInputDTO:
    user_id: int


@dataclass(frozen=True)
class UserDTO:
    user_id: int
    full_name: str
    username: str | None
    phone_number: str | None


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
                    user_id
            )
            raise UserIsNotExistError(user_id)

        logging.info(
                "GetUser: successfully get user %s",
                user_id
        )

        return UserDTO(
                user_id=user_id,
                full_name=user.full_name,
                username=user.username,
                phone_number=user.phone_number
        )
