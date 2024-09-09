import asyncio
import logging
from dataclasses import dataclass

from application.common.request_data import Pagination
from application.user.gateway import GetUsersFilters, UserReader
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from entities.user.models import User


@dataclass(frozen=True)
class GetUsersInputData:
    pagination: Pagination
    filters: GetUsersFilters


@dataclass
class GetUsersOutputData:
    total: int
    users: list[User]


class GetUsers(Interactor[GetUsersInputData, GetUsersOutputData]):
    def __init__(
            self,
            user_reader: UserReader,
            id_provider: IdentityProvider
    ):
        self._user_reader = user_reader
        self._id_provider = id_provider

    async def __call__(
            self,
            data: GetUsersInputData
    ) -> GetUsersOutputData:
        total_users: int = await asyncio.create_task(
                self._user_reader.total_users(data.filters)
        )
        users: list[User] = await asyncio.create_task(
                self._user_reader.all(
                        data.filters,
                        data.pagination
                )
        )

        logging.info(
                "Get user",
                extra={
                    "user": users,
                    "pagination": data.pagination,
                    "filters": data.filters
                }
        )

        return GetUsersOutputData(total=total_users, users=users)
