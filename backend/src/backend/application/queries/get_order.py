from backend.application.dto.gateways.order_gateway import (
    OrderReadModel,
)
from backend.application.errors import EntityNotFoundError
from backend.application.vars import OrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyOrderGateway


class GetOrderQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway

    async def handle(self, order_id: OrderId) -> OrderReadModel:
        current_user = await self._idp.current_user()

        if order := await self._order_gateway.read(
            order_id, current_user.shop_id
        ):
            return order
        raise EntityNotFoundError(entity="Order")
