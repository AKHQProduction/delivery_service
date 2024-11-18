import logging
from dataclasses import dataclass

from application.common.interfaces.user.gateways import UserReader
from application.common.interfaces.user.read_models import UserProfile
from application.user.errors import UserNotFoundError


@dataclass(frozen=True)
class GetUserProfileInputData:
    tg_id: int


@dataclass
class GetUserProfile:
    user_reader: UserReader

    async def __call__(self, data: GetUserProfileInputData) -> UserProfile:
        user = await self.user_reader.get_profile_with_tg_id(data.tg_id)

        if user is None:
            logging.info("GetUser: user with tg id %s not found", data.tg_id)
            raise UserNotFoundError()

        logging.info(
            "GetUser: successfully get user with tg id=%s", data.tg_id
        )

        return user
