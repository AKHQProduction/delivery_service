import logging
from dataclasses import dataclass

from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import ensure_is_owner
from backend.application.services.payment_method import create_payment_method
from backend.application.vars import PaymentMethodId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyPaymentMethodGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreatePaymentMethodCommand:
    name: str


class CreatePaymentMethodCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._payment_method_gateway = payment_method_gateway
        self._tr_manager = tr_manager

    async def handle(
        self, command: CreatePaymentMethodCommand
    ) -> PaymentMethodId:
        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        if await self._payment_method_gateway.exists_by_name_in_shop(
            current_user.shop_id, command.name
        ):
            raise AlreadyExistsError(entity="PaymentMethod")

        payment_method_id = self._payment_method_gateway.next_id()

        payment_method = create_payment_method(
            payment_method_id=payment_method_id,
            shop_id=current_user.shop_id,
            name=command.name,
        )
        self._payment_method_gateway.save(payment_method)

        await self._tr_manager.commit()

        logger.info(
            "Payment method %s created for shop %s",
            payment_method_id,
            current_user.shop_id,
        )

        return payment_method_id
