from dataclasses import dataclass
from decimal import Decimal

from backend.application.common import ensure_exists
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.client import set_client_balance
from backend.application.vars import ClientId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyClientGateway
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class SetClientBalanceCommand:
    client_id: ClientId
    balance: Decimal


class SetClientBalanceCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: SetClientBalanceCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        client = ensure_exists(
            await self._client_gateway.load(command.client_id),
            "Client",
        )
        ensure_related_to_shop(current_user, client.shop_id)

        set_client_balance(client, balance=command.balance)
        await self._tr_manager.commit()
