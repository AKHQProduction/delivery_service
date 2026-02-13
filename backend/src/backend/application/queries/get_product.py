from backend.application.dto.gateways.product_gateway import (
    ProductReadModel,
)
from backend.application.errors import EntityNotFoundError
from backend.application.vars import ProductId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)


class GetProductQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        product_gateway: SQLAlchemyProductGateway,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway

    async def handle(self, product_id: ProductId) -> ProductReadModel:
        current_user = await self._idp.current_user()

        if product := await self._product_gateway.read(
            product_id, current_user.shop_id
        ):
            return product
        raise EntityNotFoundError(entity="Product")
