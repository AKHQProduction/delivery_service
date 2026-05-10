import logging
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
from backend.application.services.recurring.occurrence_ledger import (
    RecurringOrderOccurrenceLedger,
)
from backend.application.services.recurring.scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.services.recurring.template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.vars import (
    RecurringOrderId,
    RecurringOrderStatus,
    ShopId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)

logger = logging.getLogger(__name__)


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
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        order_intake: OrderIntake,
        occurrence_ledger: RecurringOrderOccurrenceLedger,
        scheduling_clock: RecurringOrderSchedulingClock,
        template_integrity: RecurringOrderTemplateIntegrity,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway
        self._order_intake = order_intake
        self._occurrence_ledger = occurrence_ledger
        self._scheduling_clock = scheduling_clock
        self._template_integrity = template_integrity

    async def run(
        self, request: RecurringOrderExecutionRequest
    ) -> RecurringOrderExecutionResult:
        logger.info(
            "Running recurring order generation: "
            "recurring_order_id=%s shop_id=%s include_today=%s activate=%s",
            request.recurring_order_id,
            request.shop_id,
            request.include_today,
            request.activate,
        )
        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load_with_items(
                request.recurring_order_id
            ),
            "RecurringOrder",
        )
        if recurring_order.shop_id != request.shop_id:
            logger.warning(
                "Recurring order generation denied for another shop: "
                "recurring_order_id=%s template_shop_id=%s request_shop_id=%s",
                request.recurring_order_id,
                recurring_order.shop_id,
                request.shop_id,
            )
            raise AccessDeniedError

        if recurring_order.status == RecurringOrderStatus.PAUSED:
            if not request.activate:
                logger.warning(
                    "Recurring order generation rejected because template is "
                    "paused: recurring_order_id=%s",
                    recurring_order.id,
                )
                raise RecurringOrderPausedError
            logger.info(
                "Activating recurring order before generation: "
                "recurring_order_id=%s",
                recurring_order.id,
            )
            recurring_order.status = RecurringOrderStatus.ACTIVE

        if not await self._template_integrity.is_runnable(recurring_order):
            recurring_order.status = RecurringOrderStatus.PAUSED
            logger.warning(
                "Recurring order generation paused invalid template: "
                "recurring_order_id=%s",
                recurring_order.id,
            )
            return RecurringOrderExecutionResult(
                created_dates=[],
                already_scheduled_dates=[],
                cancelled_dates=[],
                paused=True,
            )

        scheduled_dates = self._scheduling_clock.run_dates(
            schedule_type=recurring_order.schedule_type,
            weekdays=recurring_order.weekdays,
            month_days=recurring_order.month_days,
            include_today=request.include_today,
        )
        occurrence_plan = await self._occurrence_ledger.plan_dates(
            recurring_order.id, scheduled_dates
        )
        logger.info(
            "Recurring order generation planned: "
            "recurring_order_id=%s candidate_dates=%d to_create=%d "
            "already_scheduled=%d cancelled=%d",
            recurring_order.id,
            len(scheduled_dates),
            len(occurrence_plan.dates_to_create),
            len(occurrence_plan.already_scheduled_dates),
            len(occurrence_plan.cancelled_dates),
        )

        created_dates: list[date] = []
        for scheduled_for in occurrence_plan.dates_to_create:
            await self._create_order_for_date(recurring_order, scheduled_for)
            created_dates.append(scheduled_for)

        result = RecurringOrderExecutionResult(
            created_dates=created_dates,
            already_scheduled_dates=occurrence_plan.already_scheduled_dates,
            cancelled_dates=occurrence_plan.cancelled_dates,
            paused=False,
        )
        logger.info(
            "Recurring order generation completed: "
            "recurring_order_id=%s created=%d already_scheduled=%d "
            "cancelled=%d",
            recurring_order.id,
            len(created_dates),
            len(occurrence_plan.already_scheduled_dates),
            len(occurrence_plan.cancelled_dates),
        )
        return result

    async def _create_order_for_date(
        self,
        recurring_order: RecurringOrder,
        scheduled_for: date,
    ) -> None:
        assert recurring_order.address_id is not None
        assert recurring_order.phone_id is not None
        assert recurring_order.time_slot_id is not None

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

        self._occurrence_ledger.mark_scheduled(
            recurring_order_id=recurring_order.id,
            scheduled_for=scheduled_for,
            order_id=order.id,
        )
        logger.info(
            "Generated order from recurring order: "
            "recurring_order_id=%s order_id=%s scheduled_for=%s",
            recurring_order.id,
            order.id,
            scheduled_for,
        )
