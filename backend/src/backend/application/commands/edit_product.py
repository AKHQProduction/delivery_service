import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.interfaces import IdentityProvider, TransactionManager
from backend.application.interfaces.gateways.product_gateway import (
    ProductGateway,
)
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import ProductCategory, ProductId

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditProductCommand:
    product_id: ProductId
    new_name: str | None = None
    new_price: int | None = None
    new_category: ProductCategory | None = None


class EditProductCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        product_gateway: ProductGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditProductCommand) -> None:
        logger.info(
            "Editing product: product_id=%s, new_name=%s, new_price=%s, "
            "new_category=%s",
            command.product_id,
            command.new_name,
            command.new_price,
            command.new_category,
        )

        current_user = await self._idp.current_user()
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when editing product %s",
                current_user,
                command.product_id,
            )
            raise AccessDeniedError

        product = await self._product_gateway.load(command.product_id)
        if not product:
            logger.warning(
                "Product not found: product_id=%s", command.product_id
            )
            raise EntityNotFoundError(entity="Product")

        if not IsRelatedToShop(product.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to edit "
                "product %s (shop_id=%s)",
                current_user,
                current_user.shop_id,
                command.product_id,
                product.shop_id,
            )
            raise AccessDeniedError

        updates = []
        if command.new_name:
            product.name = command.new_name
            updates.append(f"name={command.new_name}")
        if command.new_price:
            product.price = command.new_price
            updates.append(f"price={command.new_price}")
        if command.new_category:
            product.category = command.new_category
            updates.append(f"category={command.new_category}")

        logger.debug(
            "Updating product %s: %s", command.product_id, ", ".join(updates)
        )

        await self._product_gateway.update(product)
        await self._tr_manager.commit()

        logger.info(
            "Successfully edited product: id=%s, shop_id=%s, updates=%s",
            command.product_id,
            product.shop_id,
            ", ".join(updates),
        )
