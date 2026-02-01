import logging
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.application.errors import AccessDeniedError
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
)
from backend.application.policies.access import can_shop_manage_policy
from backend.application.vars import CategoryId, Empty, ProductId
from backend.infrastructure.idp import TelegramIdentityProvider
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
        idp: TelegramIdentityProvider,
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
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when creating product %s",
                current_user,
                command.name,
            )
            raise AccessDeniedError

        product_id = self._gateway.next_id()
        logger.debug("Generated product_id: %s", product_id)

        category_id: CategoryId | None = (
            CategoryId(command.category_id)
            if isinstance(command.category_id, UUID)
            else None
        )

        await self._gateway.create_product(
            CreateProductDTO(
                product_id=product_id,
                shop_id=current_user.shop_id,
                name=command.name,
                price=command.price,
                category_id=category_id,
            )
        )
        await self._tr_manager.commit()

        logger.info(
            "Successfully created product: id=%s, name=%s, shop_id=%s",
            product_id,
            command.name,
            current_user.shop_id,
        )
        return product_id
