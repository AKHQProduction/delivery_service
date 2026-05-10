import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.recurring_order_resource_impact import (
    RecurringOrderResourceImpact,
)
from backend.application.vars import ProductId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteProductCommand:
    product_id: ProductId


class DeleteProductCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        product_gateway: SQLAlchemyProductGateway,
        recurring_order_impact: RecurringOrderResourceImpact,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway
        self._recurring_order_impact = recurring_order_impact
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteProductCommand) -> None:
        logger.info(
            "Deleting product: product_id=%s",
            command.product_id,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        product = await self._product_gateway.load(command.product_id)
        if not product:
            return

        ensure_related_to_shop(current_user, product.shop_id)

        await self._recurring_order_impact.pause_for_deleted_product(
            product.id, current_user
        )

        await self._product_gateway.delete(product)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted product: id=%s, shop_id=%s",
            command.product_id,
            product.shop_id,
        )
