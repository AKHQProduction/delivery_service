import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.route_builder import (
    insert_order_into_route,
    remove_order_from_route,
)
from backend.application.vars import OrderId, today
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
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
        shop_gateway: SQLAlchemyShopGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._client_gateway = client_gateway
        self._shop_gateway = shop_gateway
        self._route_plan_gateway = route_plan_gateway
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

        route_plan = await self._route_plan_gateway.find_by_order(order.id)
        if route_plan:
            remove_order_from_route(route_plan, order.id)
            shop = await self._shop_gateway.load_shop(order.shop_id)
            shop_coords = CoordinatesDTO.build(
                shop.latitude if shop else None,
                shop.longitude if shop else None,
            )
            all_orders = await self._order_gateway.load_by_date(
                shop_id=order.shop_id,
                delivery_date=order.date,
                start_time=order.delivery_start_time,
                end_time=order.delivery_end_time,
            )
            insert_order_into_route(route_plan, order, shop_coords, all_orders)
            logger.info(
                "Recalculated route position for order %s in plan %s",
                order.id,
                route_plan.id,
            )

        await self._tr_manager.commit()
