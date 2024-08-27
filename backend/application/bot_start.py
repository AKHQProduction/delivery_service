import logging
from dataclasses import dataclass

from application.common.gateways.user import UserSaver, UserReader
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.commiter import Commiter
from domain.entities.user import User
from domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class BotStartDTO:
    user_id: int
    full_name: str
    username: str | None = None


class BotStart(Interactor[BotStartDTO, UserId]):
    def __init__(
            self,
            user_reader: UserReader,
            user_saver: UserSaver,
            commiter: Commiter,
            identity_provider: IdentityProvider
    ):
        self.user_reader = user_reader
        self.user_saver = user_saver
        self.commiter = commiter
        self.identity_provider = identity_provider

    async def __call__(self, data: BotStartDTO) -> UserId:
        user = await self.identity_provider.get_user()

        if not user:
            await self.user_saver.save(
                    User(
                            user_id=UserId(data.user_id),
                            full_name=data.full_name,
                            username=data.username
                    )
            )

            await self.commiter.commit()

            logging.info("New user created %s", data.user_id)

        logging.info("Get user %s", data.user_id)

        return UserId(data.user_id)
