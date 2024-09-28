import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.user.gateway import UserReader, UserSaver
from entities.user.models import User, UserId


@dataclass(frozen=True)
class AdminBotStartInputData:
    user_id: int
    full_name: str
    username: str | None


class AdminBotStart(Interactor[AdminBotStartInputData, UserId]):
    def __init__(
        self,
        user_reader: UserReader,
        user_saver: UserSaver,
        commiter: Commiter,
        identity_provider: IdentityProvider,
    ):
        self._user_reader = user_reader
        self._user_saver = user_saver
        self._commiter = commiter
        self._identity_provider = identity_provider

    async def __call__(self, data: AdminBotStartInputData) -> UserId:
        actor = await self._identity_provider.get_user()

        if actor:
            logging.info("Get user %s", data.user_id)
            return actor.user_id

        await self._user_saver.save(
            User(
                user_id=UserId(data.user_id),
                full_name=data.full_name,
                username=data.username,
            ),
        )

        await self._commiter.commit()

        logging.info("New user created %s", data.user_id)

        return UserId(data.user_id)
