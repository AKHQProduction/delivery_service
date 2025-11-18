import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError
from backend.application.interfaces import (
    IdentityProvider,
    TransactionManager,
)
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    ProductGateway,
)
from backend.application.policies.access import can_shop_manage_policy
from backend.application.vars import ProductCategory, ProductId

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateProductCommand:
    name: str
    price: int
    category: ProductCategory


class CreateProductCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        gateway: ProductGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._gateway = gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateProductCommand) -> ProductId:
        logger.info(
            "Creating product: name=%s, price=%d, category=%s",
            command.name,
            command.price,
            command.category,
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

        await self._gateway.create_product(
            CreateProductDTO(
                product_id=product_id,
                shop_id=current_user.shop_id,
                name=command.name,
                price=command.price,
                category=command.category,
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
