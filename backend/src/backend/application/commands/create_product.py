import logging
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.application.policies.access import ensure_can_manage
from backend.application.services.product import create_product
from backend.application.vars import CategoryId, Empty, ProductId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateProductCommand:
    name: str
    price: Decimal
    category_id: CategoryId | Empty = Empty.EMPTY


class CreateProductCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        gateway: SQLAlchemyProductGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._gateway = gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateProductCommand) -> ProductId:
        logger.info(
            "Creating product: name=%s, price=%d, category_id=%s",
            command.name,
            command.price,
            command.category_id,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        product_id = self._gateway.next_id()

        category_id: CategoryId | None = (
            CategoryId(command.category_id)
            if isinstance(command.category_id, UUID)
            else None
        )

        product = create_product(
            product_id=product_id,
            shop_id=current_user.shop_id,
            name=command.name,
            price=command.price,
            category_id=category_id,
        )
        self._gateway.save(product)
        await self._tr_manager.commit()

        logger.info(
            "Successfully created product: id=%s, name=%s, shop_id=%s",
            product_id,
            command.name,
            current_user.shop_id,
        )
        return product_id
