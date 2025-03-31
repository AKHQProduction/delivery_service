import logging
from dataclasses import dataclass

from application.common.identity_provider import IdentityProvider
from application.common.transaction_manager import TransactionManager
from entities.user.services import UserService


@dataclass(frozen=True)
class AdminBotStartCommand:
    tg_id: int
    full_name: str
    username: str | None


@dataclass
class AdminBotStartCommandHandler:
    identity_provider: IdentityProvider
    user_service: UserService
    transaction_manager: TransactionManager

    async def __call__(self, command: AdminBotStartCommand) -> None:
        actor = await self.identity_provider.get_user()

        if not actor:
            new_user = self.user_service.create_new_user(
                command.full_name, command.username, command.tg_id
            )

            await self.transaction_manager.commit()

            logging.info("New user created %s", new_user.oid)
