import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interfaces.user.gateways import UserGateway
from entities.user.services import create_user


@dataclass(frozen=True)
class AdminBotStartInputData:
    tg_id: int
    full_name: str
    username: str | None


@dataclass
class AdminBotStart:
    user_mapper: UserGateway
    commiter: Commiter
    identity_provider: IdentityProvider

    async def __call__(self, data: AdminBotStartInputData) -> None:
        logging.info("Handle start command from admin bot")
        actor = await self.identity_provider.get_user()

        if not actor:
            logging.info("User not found, try to create new")
            new_user = create_user(data.full_name, data.username, data.tg_id)

            await self.user_mapper.add_one(new_user)
            await self.commiter.commit()

            logging.info("New user created %s", new_user.user_id)
