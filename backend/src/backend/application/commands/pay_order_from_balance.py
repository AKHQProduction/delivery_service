from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import (
    AccessDeniedError,
)
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.order_payment import (
    apply_balance_payment,
)
from backend.application.vars import OrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class PayOrderFromBalanceCommand:
    order_id: OrderId


class PayOrderFromBalanceCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        client_gateway: SQLAlchemyClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: PayOrderFromBalanceCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = ensure_exists(
            await self._order_gateway.load_with_items_for_update(
                command.order_id
            ),
            "Order",
        )
        ensure_related_to_shop(current_user, order.shop_id)

        client = ensure_exists(
            await self._client_gateway.load_for_update(order.client_id),
            "Client",
        )
        if client.shop_id != order.shop_id:
            raise AccessDeniedError

        apply_balance_payment(order, client)

        await self._tr_manager.commit()
