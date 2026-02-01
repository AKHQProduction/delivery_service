import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import ClientId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyClientGateway
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteClientCommand:
    client_id: ClientId


class DeleteClientCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteClientCommand) -> None:
        logger.info(
            "Deleting client: client_id=%s",
            command.client_id,
        )

        current_user = await self._idp.current_user()
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when deleting client %s",
                current_user,
                command.client_id,
            )
            raise AccessDeniedError

        client = await self._client_gateway.load(command.client_id)
        if not client:
            logger.warning("Client not found: client_id=%s", command.client_id)
            return

        if not IsRelatedToShop(client.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to delete "
                "client %s (shop_id=%s)",
                current_user,
                current_user.shop_id,
                command.client_id,
                client.shop_id,
            )
            raise AccessDeniedError

        await self._client_gateway.delete(command.client_id)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted client: id=%s, shop_id=%s",
            command.client_id,
            client.shop_id,
        )
