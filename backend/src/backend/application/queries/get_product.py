from backend.application.errors import EntityNotFoundError
from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways.product_gateway import (
    ProductGateway,
    ProductReadModel,
)
from backend.application.vars import ProductId


class GetProduct:
    def __init__(
        self, idp: IdentityProvider, product_gateway: ProductGateway
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway

    async def handle(self, product_id: ProductId) -> ProductReadModel:
        await self._idp.current_user()

        if product := await self._product_gateway.read(product_id):
            return product
        raise EntityNotFoundError(entity="Product")
