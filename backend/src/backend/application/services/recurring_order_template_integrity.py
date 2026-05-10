from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)


class RecurringOrderTemplateIntegrity:
    def __init__(
        self,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
    ) -> None:
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._time_slot_gateway = time_slot_gateway

    async def is_runnable(self, recurring_order: RecurringOrder) -> bool:
        if (
            recurring_order.address_id is None
            or recurring_order.phone_id is None
            or recurring_order.time_slot_id is None
            or not recurring_order.items
        ):
            return False

        client = await self._client_gateway.load(recurring_order.client_id)
        if client is None or client.shop_id != recurring_order.shop_id:
            return False
        if not any(
            address.id == recurring_order.address_id
            for address in client.addresses
        ):
            return False
        if not any(
            phone.id == recurring_order.phone_id for phone in client.phones
        ):
            return False

        time_slot = await self._time_slot_gateway.load(
            recurring_order.time_slot_id
        )
        if time_slot is None or time_slot.shop_id != recurring_order.shop_id:
            return False

        product_ids = {item.product_id for item in recurring_order.items}
        products = await self._product_gateway.load_many(list(product_ids))
        return {
            product.id
            for product in products
            if product.shop_id == recurring_order.shop_id
        } == product_ids
