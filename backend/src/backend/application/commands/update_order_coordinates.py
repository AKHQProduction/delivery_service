import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import OrderId, today
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateOrderCoordinatesCommand:
    order_id: OrderId
    latitude: float
    longitude: float


class UpdateOrderCoordinatesCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        client_gateway: SQLAlchemyClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: UpdateOrderCoordinatesCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = ensure_exists(
            await self._order_gateway.load(command.order_id),
            "Order",
        )
        ensure_related_to_shop(current_user, order.shop_id)

        new_coords = CoordinatesDTO(
            latitude=command.latitude,
            longitude=command.longitude,
        )

        addr = ensure_exists(order.delivery_address, "DeliveryAddress")
        addr.coordinates = new_coords
        order.delivery_address = addr

        client = await self._client_gateway.load(order.client_id)
        if client:
            for client_addr in client.addresses:
                if (
                    client_addr.street.strip().lower()
                    == addr.street.strip().lower()
                    and client_addr.house.strip().lower()
                    == addr.house.strip().lower()
                ):
                    client_addr.latitude = new_coords.latitude
                    client_addr.longitude = new_coords.longitude
                    break

        updated = await self._order_gateway.update_delivery_coordinates(
            shop_id=order.shop_id,
            client_id=order.client_id,
            street=addr.street,
            house=addr.house,
            new_coordinates=new_coords,
            from_date=today(),
        )

        if updated:
            logger.info(
                "Propagated coordinates to %d order(s) for "
                "order_id=%s, client_id=%s",
                updated,
                command.order_id,
                order.client_id,
            )

        await self._tr_manager.commit()
