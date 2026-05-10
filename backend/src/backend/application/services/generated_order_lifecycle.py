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
        occurrence = (
            await self._recurring_order_gateway.load_occurrence_by_filters(
                RecurringOrderOccurrenceFilters(order_id=order_id)
            )
        )
        if occurrence:
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

        await self._order_deletion.delete(order_id, current_user)

    async def delete_future_orders(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
        current_user: CurrentUserDTO,
    ) -> None:
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

    async def delete_future_orders_for_rebuild(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
        current_user: CurrentUserDTO,
    ) -> None:
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
