import asyncio
import logging
from dataclasses import dataclass

from application.common.input_data import Pagination
from application.common.interactor import Interactor
from application.user.gateway import GetUsersFilters, UserReader
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
    ):
        self._user_reader = user_reader

    async def __call__(self, data: GetUsersInputData) -> GetUsersOutputData:
        total_users: int = await asyncio.create_task(
            self._user_reader.total(data.filters),
        )
        users: list[User] = await asyncio.create_task(
            self._user_reader.all(data.filters, data.pagination),
        )

        logging.info(
            "Get user",
            extra={
                "user": users,
                "pagination": data.pagination,
                "filters": data.filters,
            },
        )

        return GetUsersOutputData(total=total_users, users=users)
