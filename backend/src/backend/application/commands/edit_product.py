import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import CategoryId, Empty, ProductId
from backend.domain.services.product import update_product
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditProductCommand:
    product_id: ProductId
    new_name: str | None = None
    new_price: Decimal | None = None
    new_category_id: CategoryId | Empty | None = None


class EditProductCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        product_gateway: SQLAlchemyProductGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditProductCommand) -> None:
        logger.info(
            "Editing product: product_id=%s, new_name=%s, new_price=%s, "
            "new_category_id=%s",
            command.product_id,
            command.new_name,
            command.new_price,
            command.new_category_id,
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

        new_category_id: CategoryId | Empty | None = Empty.EMPTY
        updates = []
        if command.new_name:
            updates.append(f"name={command.new_name}")
        if command.new_price is not None:
            updates.append(f"price={command.new_price}")
        if command.new_category_id is not None:
            if command.new_category_id == Empty.EMPTY:
                new_category_id = None
                updates.append("category_id=None")
            else:
                new_category_id = cast("CategoryId", command.new_category_id)
                updates.append(f"category_id={command.new_category_id}")

        logger.debug(
            "Updating product %s: %s",
            command.product_id,
            ", ".join(updates),
        )

        update_product(
            product,
            name=command.new_name,
            price=command.new_price,
            category_id=new_category_id,
        )
        await self._tr_manager.commit()

        logger.info(
            "Successfully edited product: id=%s, shop_id=%s, updates=%s",
            command.product_id,
            product.shop_id,
            ", ".join(updates),
        )
