import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import ProductId
from backend.infrastructure.idp import TelegramIdentityProvider
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
        idp: TelegramIdentityProvider,
        product_gateway: SQLAlchemyProductGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteProductCommand) -> None:
        logger.info(
            "Deleting product: product_id=%s",
            command.product_id,
        )

        current_user = await self._idp.current_user()
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when deleting product %s",
                current_user,
                command.product_id,
            )
            raise AccessDeniedError

        product = await self._product_gateway.load(command.product_id)
        if not product:
            logger.warning(
                "Product not found: product_id=%s", command.product_id
            )
            return

        if not IsRelatedToShop(product.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to delete "
                "product %s (shop_id=%s)",
                current_user,
                current_user.shop_id,
                command.product_id,
                product.shop_id,
            )
            raise AccessDeniedError

        await self._product_gateway.delete(command.product_id)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted product: id=%s, shop_id=%s",
            command.product_id,
            product.shop_id,
        )
