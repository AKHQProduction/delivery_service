import logging

from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)

logger = logging.getLogger(__name__)


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
            logger.info(
                "Recurring order template is not runnable because required "
                "fields are missing: recurring_order_id=%s address_id=%s "
                "phone_id=%s time_slot_id=%s items_count=%d",
                recurring_order.id,
                recurring_order.address_id,
                recurring_order.phone_id,
                recurring_order.time_slot_id,
                len(recurring_order.items),
            )
            return False

        client = await self._client_gateway.load(recurring_order.client_id)
        if client is None or client.shop_id != recurring_order.shop_id:
            logger.info(
                "Recurring order template is not runnable because client is "
                "missing or belongs to another shop: recurring_order_id=%s "
                "client_id=%s",
                recurring_order.id,
                recurring_order.client_id,
            )
            return False
        if not any(
            address.id == recurring_order.address_id
            for address in client.addresses
        ):
            logger.info(
                "Recurring order template is not runnable because address is "
                "missing: recurring_order_id=%s address_id=%s",
                recurring_order.id,
                recurring_order.address_id,
            )
            return False
        if not any(
            phone.id == recurring_order.phone_id for phone in client.phones
        ):
            logger.info(
                "Recurring order template is not runnable because phone is "
                "missing: recurring_order_id=%s phone_id=%s",
                recurring_order.id,
                recurring_order.phone_id,
            )
            return False

        time_slot = await self._time_slot_gateway.load(
            recurring_order.time_slot_id
        )
        if time_slot is None or time_slot.shop_id != recurring_order.shop_id:
            logger.info(
                "Recurring order template is not runnable because time slot "
                "is missing or belongs to another shop: "
                "recurring_order_id=%s time_slot_id=%s",
                recurring_order.id,
                recurring_order.time_slot_id,
            )
            return False

        product_ids = {item.product_id for item in recurring_order.items}
        products = await self._product_gateway.load_many(list(product_ids))
        is_runnable = {
            product.id
            for product in products
            if product.shop_id == recurring_order.shop_id
        } == product_ids
        if not is_runnable:
            logger.info(
                "Recurring order template is not runnable because some "
                "products are missing or belong to another shop: "
                "recurring_order_id=%s product_ids=%s",
                recurring_order.id,
                list(product_ids),
            )
        else:
            logger.debug(
                "Recurring order template is runnable: recurring_order_id=%s",
                recurring_order.id,
            )
        return is_runnable
