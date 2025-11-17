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
        current_user = await self._idp.current_user()

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            raise AccessDeniedError

        product_id = self._gateway.next_id()
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

        return product_id
