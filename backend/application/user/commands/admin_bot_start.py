import logging
from dataclasses import dataclass

from application.common.identity_provider import IdentityProvider
from application.common.interfaces.user.gateways import UserGateway
from application.common.transaction_manager import TransactionManager
from entities.user.services import UserService


@dataclass(frozen=True)
class AdminBotStartCommand:
    tg_id: int
    full_name: str
    username: str | None


@dataclass
class AdminBotStartCommandHandler:
    user_service: UserService
    user_mapper: UserGateway
    transaction_manager: TransactionManager
    identity_provider: IdentityProvider

    async def __call__(self, command: AdminBotStartCommand) -> None:
        logging.info("Handle start command from admin bot")
        actor = await self.identity_provider.get_user()

        if not actor:
            logging.info("User not found, try to create new")
            new_user = self.user_service.create_new_user(
                command.full_name, command.username, command.tg_id
            )

            await self.transaction_manager.commit()

            logging.info("New user created %s", new_user.oid)
