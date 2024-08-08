import logging
from dataclasses import dataclass

from backend.application.common.gateways.user import UserSaver, UserReader
from backend.application.common.interactor import Interactor
from backend.domain.entities.user import User
from backend.domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class BotStartDTO:
    user_id: int
    full_name: str
    username: str | None = None


class BotStart(Interactor[BotStartDTO, UserId]):
    def __init__(
            self,
            user_reader: UserReader,
            user_saver: UserSaver
    ):
        self.user_reader = user_reader
        self.user_saver = user_saver

    async def __call__(self, data: BotStartDTO) -> UserId:
        user_id: UserId = UserId(data.user_id)

        user = await self.user_reader.by_id(user_id)

        if not user:
            await self.user_saver.save(
                User(
                    user_id=user_id,
                    full_name=data.full_name,
                    username=data.username
                )
            )

            logging.info("New user created %s", user_id.to_raw())

        logging.info("Get user %s", user_id.to_raw())

        return user_id
