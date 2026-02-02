import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import ClientId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
)
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
        ensure_can_manage(current_user)

        client = await self._client_gateway.load(command.client_id)
        if not client:
            return

        ensure_related_to_shop(current_user, client.shop_id)

        await self._client_gateway.delete(client)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted client: id=%s, shop_id=%s",
            command.client_id,
            client.shop_id,
        )
