import asyncio
import logging
from dataclasses import dataclass

from application.common.dto import Pagination
from application.common.gateways.user import GetUsersFilters, UserReader
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.errors.access import AccessDeniedError
from application.specs.has_role import HasRoleSpec
from domain.entities.user import RoleName, User


@dataclass(frozen=True)
class GetUsersDTO:
    pagination: Pagination
    filters: GetUsersFilters


@dataclass
class GetUsersResultDTO:
    total: int
    users: list[User]


class GetUsers(Interactor[GetUsersDTO, GetUsersResultDTO]):
    def __init__(
            self,
            user_reader: UserReader,
            id_provider: IdentityProvider
    ):
        self._user_reader = user_reader
        self._id_provider = id_provider

    async def __call__(self, data: GetUsersDTO) -> GetUsersResultDTO:
        actor_role = await self._id_provider.get_user_role()

        rule: Specification = (
                HasRoleSpec(RoleName.ADMIN) or HasRoleSpec(RoleName.MANAGER)
        )

        if not rule.is_satisfied_by(actor_role):
            logging.info(
                    "GetUsers: access denied to user with role %s",
                    actor_role
            )
            raise AccessDeniedError()

        total_users: int = await asyncio.create_task(
                self._user_reader.total_users(data.filters)
        )
        users: list[User] = await asyncio.create_task(
                self._user_reader.all(
                        data.filters,
                        data.pagination
                )
        )

        logging.debug(
                "Get users",
                extra={
                    "users": users,
                    "pagination": data.pagination,
                    "filters": data.filters
                }
        )

        return GetUsersResultDTO(total=total_users, users=users)
