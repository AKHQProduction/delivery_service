import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from backend.application.common import ensure_exists
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.product import update_product
from backend.application.vars import CategoryId, Empty, ProductId
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
        ensure_can_manage(current_user)

        product = ensure_exists(
            await self._product_gateway.load(command.product_id),
            "Product",
        )
        ensure_related_to_shop(current_user, product.shop_id)

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
