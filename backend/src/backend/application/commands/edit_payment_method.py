import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import (
    AlreadyExistsError,
    ProtectedPaymentMethodError,
)
from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.services.payment_method import (
    is_balance_payment_method,
    update_payment_method,
)
from backend.application.vars import PaymentMethodId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyPaymentMethodGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditPaymentMethodCommand:
    payment_method_id: PaymentMethodId
    payment_method_name: str | None = None


class EditPaymentMethodCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._payment_method_gateway = payment_method_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditPaymentMethodCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        payment_method = ensure_exists(
            await self._payment_method_gateway.load(command.payment_method_id),
            "PaymentMethod",
        )
        ensure_related_to_shop(current_user, payment_method.shop_id)

        if (
            command.payment_method_name is not None
            and command.payment_method_name != payment_method.name
            and is_balance_payment_method(payment_method=payment_method)
        ):
            raise ProtectedPaymentMethodError

        if (
            command.payment_method_name is not None
            and command.payment_method_name != payment_method.name
            and await self._payment_method_gateway.exists_by_name_in_shop(
                current_user.shop_id, command.payment_method_name
            )
        ):
            raise AlreadyExistsError(entity="PaymentMethod")

        update_payment_method(
            payment_method,
            name=command.payment_method_name,
        )

        await self._tr_manager.commit()

        logger.info("Payment method %s updated", command.payment_method_id)
