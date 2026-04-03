import logging

from backend.application.dto.gateways.payment_method_gateway import (
    PaymentMethodReadModel,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyPaymentMethodGateway,
)

logger = logging.getLogger(__name__)


class GetPaymentMethodsQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
    ) -> None:
        self._idp = idp
        self._payment_method_gateway = payment_method_gateway

    async def handle(self) -> list[PaymentMethodReadModel]:
        current_user = await self._idp.current_user()

        payment_methods = await self._payment_method_gateway.load_by_shop(
            current_user.shop_id
        )

        logger.info(
            "Retrieved %d payment methods for shop %s",
            len(payment_methods),
            current_user.shop_id,
        )

        return payment_methods
