import logging
from datetime import date

from backend.application.dto.idp import CurrentUserDTO
from backend.application.policies.access import ensure_related_to_shop
from backend.application.services.order_deletion import OrderDeletion
from backend.application.vars import (
    OrderId,
    RecurringOrderId,
    RecurringOrderOccurrenceStatus,
    RecurringOrderStatus,
)
from backend.infrastructure.persistence.gateways import (
    RecurringOrderOccurrenceFilters,
    SQLAlchemyRecurringOrderGateway,
)

logger = logging.getLogger(__name__)


class GeneratedOrderLifecycle:
    def __init__(
        self,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        order_deletion: OrderDeletion,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway
        self._order_deletion = order_deletion

    async def delete_order(
        self,
        order_id: OrderId,
        current_user: CurrentUserDTO,
        *,
        pause_recurring_order: bool = False,
    ) -> None:
        logger.info(
            "Deleting order through generated order lifecycle: "
            "order_id=%s pause_recurring_order=%s",
            order_id,
            pause_recurring_order,
        )
        occurrence = (
            await self._recurring_order_gateway.load_occurrence_by_filters(
                RecurringOrderOccurrenceFilters(order_id=order_id)
            )
        )
        if occurrence:
            logger.info(
                "Cancelling recurring order occurrence for deleted order: "
                "recurring_order_id=%s scheduled_for=%s order_id=%s",
                occurrence.recurring_order_id,
                occurrence.scheduled_for,
                order_id,
            )
            occurrence.status = RecurringOrderOccurrenceStatus.CANCELLED
            occurrence.order_id = None
            if pause_recurring_order:
                recurring_order = await self._recurring_order_gateway.load(
                    occurrence.recurring_order_id
                )
                if recurring_order is not None:
                    ensure_related_to_shop(
                        current_user, recurring_order.shop_id
                    )
                    recurring_order.status = RecurringOrderStatus.PAUSED
                    logger.info(
                        "Paused recurring order after generated order "
                        "deletion: "
                        "recurring_order_id=%s order_id=%s",
                        recurring_order.id,
                        order_id,
                    )

        await self._order_deletion.delete(order_id, current_user)

    async def delete_future_orders(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
        current_user: CurrentUserDTO,
    ) -> None:
        logger.info(
            "Deleting future generated orders: "
            "recurring_order_id=%s from_date=%s",
            recurring_order_id,
            from_date,
        )
        gateway = self._recurring_order_gateway
        occurrences = await gateway.load_occurrences_by_filters(
            RecurringOrderOccurrenceFilters(
                recurring_order_id=recurring_order_id,
                from_date=from_date,
            )
        )
        for occurrence in occurrences:
            if occurrence.order_id is not None:
                await self.delete_order(occurrence.order_id, current_user)
        logger.info(
            "Future generated orders deleted: "
            "recurring_order_id=%s from_date=%s occurrences=%d",
            recurring_order_id,
            from_date,
            len(occurrences),
        )

    async def delete_future_orders_for_rebuild(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
        current_user: CurrentUserDTO,
    ) -> None:
        logger.info(
            "Deleting future generated orders for rebuild: "
            "recurring_order_id=%s from_date=%s",
            recurring_order_id,
            from_date,
        )
        gateway = self._recurring_order_gateway
        occurrences = await gateway.load_occurrences_by_filters(
            RecurringOrderOccurrenceFilters(
                recurring_order_id=recurring_order_id,
                from_date=from_date,
                with_order=True,
            )
        )
        for occurrence in occurrences:
            if occurrence.order_id is not None:
                await self.delete_order(occurrence.order_id, current_user)

        await gateway.delete_occurrences_from(recurring_order_id, from_date)
        logger.info(
            "Future generated orders and occurrences deleted for rebuild: "
            "recurring_order_id=%s from_date=%s orders=%d",
            recurring_order_id,
            from_date,
            len(occurrences),
        )
