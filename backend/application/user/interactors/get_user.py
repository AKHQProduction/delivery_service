import logging
from dataclasses import dataclass

from application.common.interactor import Interactor
from application.user.errors import UserNotFoundError
from application.user.gateway import UserReader
from entities.user.models import UserId


@dataclass(frozen=True)
class GetUserInputData:
    user_id: int


@dataclass(frozen=True)
class GetUserOutputData:
    user_id: int
    full_name: str
    username: str | None


class GetUser(Interactor[GetUserInputData, GetUserOutputData]):
    def __init__(
        self,
        user_reader: UserReader,
    ):
        self._user_reader = user_reader

    async def __call__(self, data: GetUserInputData) -> GetUserOutputData:
        user_id = UserId(data.user_id)

        user = await self._user_reader.by_id(user_id)

        if user is None:
            logging.info("GetUser: user with id %s not found", user_id)
            raise UserNotFoundError(user_id)

        logging.info("GetUser: successfully get user with id=%s", user_id)

        return GetUserOutputData(
            user_id=user_id,
            full_name=user.full_name,
            username=user.username,
        )
