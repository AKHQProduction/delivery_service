from backend.application.dto.idp import CurrentUserDTO
from backend.application.policies.access import ensure_related_to_shop
from backend.application.vars import (
    ProductId,
    RecurringOrderStatus,
    TimeSlotId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)


class RecurringOrderResourceImpact:
    def __init__(
        self,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway

    async def pause_for_deleted_product(
        self,
        product_id: ProductId,
        current_user: CurrentUserDTO,
    ) -> None:
        recurring_orders = await self._recurring_order_gateway.load_by_product(
            product_id
        )
        for recurring_order in recurring_orders:
            ensure_related_to_shop(current_user, recurring_order.shop_id)
            recurring_order.status = RecurringOrderStatus.PAUSED

    async def pause_for_deleted_time_slot(
        self,
        time_slot_id: TimeSlotId,
        current_user: CurrentUserDTO,
    ) -> None:
        recurring_orders = (
            await self._recurring_order_gateway.load_by_time_slot(time_slot_id)
        )
        for recurring_order in recurring_orders:
            ensure_related_to_shop(current_user, recurring_order.shop_id)
            recurring_order.status = RecurringOrderStatus.PAUSED
            recurring_order.time_slot_id = None
