from dataclasses import dataclass
from datetime import date

from backend.application.common import ensure_exists
from backend.application.errors import (
    AccessDeniedError,
    RecurringOrderPausedError,
)
from backend.application.services.order_intake import (
    OrderIntake,
    OrderIntakeItem,
    OrderIntakeRequest,
)
from backend.application.services.recurring_order_schedule import (
    iter_recurring_order_dates,
)
from backend.application.vars import (
    RecurringOrderId,
    RecurringOrderOccurrenceStatus,
    RecurringOrderStatus,
    ShopId,
    today,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyRecurringOrderGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderOccurrence,
)


@dataclass(frozen=True)
class RecurringOrderExecutionRequest:
    recurring_order_id: RecurringOrderId
    shop_id: ShopId
    include_today: bool = False
    activate: bool = False


@dataclass(frozen=True)
class RecurringOrderExecutionResult:
    created_dates: list[date]
    already_scheduled_dates: list[date]
    cancelled_dates: list[date]
    paused: bool


class RecurringOrderExecution:
    def __init__(
        self,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        order_intake: OrderIntake,
    ) -> None:
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._recurring_order_gateway = recurring_order_gateway
        self._time_slot_gateway = time_slot_gateway
        self._order_intake = order_intake

    async def run(
        self, request: RecurringOrderExecutionRequest
    ) -> RecurringOrderExecutionResult:
        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load_with_items(
                request.recurring_order_id
            ),
            "RecurringOrder",
        )
        if recurring_order.shop_id != request.shop_id:
            raise AccessDeniedError

        if recurring_order.status == RecurringOrderStatus.PAUSED:
            if not request.activate:
                raise RecurringOrderPausedError
            recurring_order.status = RecurringOrderStatus.ACTIVE

        if not await self._has_required_links(recurring_order):
            recurring_order.status = RecurringOrderStatus.PAUSED
            return RecurringOrderExecutionResult(
                created_dates=[],
                already_scheduled_dates=[],
                cancelled_dates=[],
                paused=True,
            )

        scheduled_dates = iter_recurring_order_dates(
            schedule_type=recurring_order.schedule_type,
            weekdays=recurring_order.weekdays,
            month_days=recurring_order.month_days,
            base_date=today(),
            include_today=request.include_today,
        )
        existing_occurrences = {
            occurrence.scheduled_for: occurrence
            for occurrence in (
                await self._recurring_order_gateway.load_occurrences_for_dates(
                    recurring_order.id, scheduled_dates
                )
            )
        }

        created_dates: list[date] = []
        already_scheduled_dates: list[date] = []
        cancelled_dates: list[date] = []
        for scheduled_for in scheduled_dates:
            existing = existing_occurrences.get(scheduled_for)
            if existing is not None:
                if existing.status == RecurringOrderOccurrenceStatus.CANCELLED:
                    cancelled_dates.append(scheduled_for)
                else:
                    already_scheduled_dates.append(scheduled_for)
                continue

            await self._create_order_for_date(recurring_order, scheduled_for)
            created_dates.append(scheduled_for)

        return RecurringOrderExecutionResult(
            created_dates=created_dates,
            already_scheduled_dates=already_scheduled_dates,
            cancelled_dates=cancelled_dates,
            paused=False,
        )

    async def _create_order_for_date(
        self,
        recurring_order: RecurringOrder,
        scheduled_for: date,
    ) -> None:
        assert recurring_order.address_id is not None
        assert recurring_order.phone_id is not None

        order = await self._order_intake.create(
            recurring_order.shop_id,
            OrderIntakeRequest(
                client_id=recurring_order.client_id,
                delivery_date=scheduled_for,
                time_slot_id=recurring_order.time_slot_id,
                address_id=recurring_order.address_id,
                phone_id=recurring_order.phone_id,
                products=[
                    OrderIntakeItem(
                        product_id=item.product_id,
                        quantity=item.quantity,
                    )
                    for item in recurring_order.items
                ],
                payment_method=recurring_order.payment_method,
                comment=recurring_order.comment,
                recurring_order_id=recurring_order.id,
            ),
        )

        self._recurring_order_gateway.save_occurrence(
            RecurringOrderOccurrence(
                recurring_order_id=recurring_order.id,
                scheduled_for=scheduled_for,
                status=RecurringOrderOccurrenceStatus.SCHEDULED,
                order_id=order.id,
            )
        )

    async def _has_required_links(
        self, recurring_order: RecurringOrder
    ) -> bool:
        if (
            recurring_order.address_id is None
            or recurring_order.phone_id is None
        ):
            return False

        client = await self._client_gateway.load(recurring_order.client_id)
        if client is None:
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
        if time_slot is None:
            return False

        product_ids = {item.product_id for item in recurring_order.items}
        products = await self._product_gateway.load_many(list(product_ids))
        return {product.id for product in products} == product_ids
