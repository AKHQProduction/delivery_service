import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import (
    LastPaymentMethodError,
    ProtectedPaymentMethodError,
)
from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.services.payment_method import (
    is_balance_payment_method,
)
from backend.application.vars import PaymentMethodId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyPaymentMethodGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletePaymentMethodCommand:
    payment_method_id: PaymentMethodId


class DeletePaymentMethodCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._payment_method_gateway = payment_method_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeletePaymentMethodCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        payment_method = ensure_exists(
            await self._payment_method_gateway.load(command.payment_method_id),
            "PaymentMethod",
        )
        ensure_related_to_shop(current_user, payment_method.shop_id)

        if is_balance_payment_method(payment_method=payment_method):
            raise ProtectedPaymentMethodError

        count = await self._payment_method_gateway.count_by_shop(
            payment_method.shop_id
        )
        if count <= 1:
            raise LastPaymentMethodError

        await self._payment_method_gateway.delete(payment_method)

        await self._tr_manager.commit()

        logger.info("Payment method %s deleted", command.payment_method_id)
