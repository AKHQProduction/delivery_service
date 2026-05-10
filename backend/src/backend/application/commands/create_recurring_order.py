import logging
from dataclasses import dataclass

from backend.application.policies.access import ensure_can_manage
from backend.application.services.recurring.template_write import (
    RecurringOrderProductInput,
    RecurringOrderTemplateDraft,
    RecurringOrderTemplateWritePolicy,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    RecurringOrderId,
    ScheduleType,
    TimeSlotId,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateRecurringOrderCommand:
    client_id: ClientId
    address_id: AddressId
    phone_id: PhoneId
    time_slot_id: TimeSlotId
    items: list[RecurringOrderProductInput]
    payment_method: str
    schedule_type: ScheduleType
    weekdays: list[int] | None = None
    month_days: list[int] | None = None
    comment: str | None = None


class CreateRecurringOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        template_write: RecurringOrderTemplateWritePolicy,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._recurring_order_gateway = recurring_order_gateway
        self._template_write = template_write
        self._tr_manager = tr_manager

    async def handle(
        self, command: CreateRecurringOrderCommand
    ) -> RecurringOrderId:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        recurring_order_id = self._recurring_order_gateway.next_id()
        recurring_order = await self._template_write.create(
            recurring_order_id=recurring_order_id,
            shop_id=current_user.shop_id,
            draft=RecurringOrderTemplateDraft(
                client_id=command.client_id,
                address_id=command.address_id,
                phone_id=command.phone_id,
                time_slot_id=command.time_slot_id,
                items=command.items,
                payment_method=command.payment_method,
                schedule_type=command.schedule_type,
                weekdays=command.weekdays,
                month_days=command.month_days,
                comment=command.comment,
            ),
        )

        self._recurring_order_gateway.save(recurring_order)
        await self._tr_manager.flush()
        await self._tr_manager.commit()

        logger.info("Recurring order %s created", recurring_order_id)
        return recurring_order_id
