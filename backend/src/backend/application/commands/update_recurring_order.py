import logging
from dataclasses import dataclass

from backend.application.commands.create_recurring_order import (
    RecurringOrderProductInput,
)
from backend.application.common import ensure_exists
from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.recurring_order import (
    normalize_schedule,
    validate_items,
)
from backend.application.vars import (
    AddressId,
    PhoneId,
    RecurringOrderId,
    ScheduleType,
    TimeSlotId,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyPaymentMethodGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyRecurringOrderGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrderItem,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateRecurringOrderCommand:
    recurring_order_id: RecurringOrderId
    address_id: AddressId
    phone_id: PhoneId
    time_slot_id: TimeSlotId
    items: list[RecurringOrderProductInput]
    payment_method: str
    schedule_type: ScheduleType
    weekdays: list[int] | None = None
    month_days: list[int] | None = None
    comment: str | None = None


class UpdateRecurringOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._recurring_order_gateway = recurring_order_gateway
        self._time_slot_gateway = time_slot_gateway
        self._payment_method_gateway = payment_method_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: UpdateRecurringOrderCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load_with_items(
                command.recurring_order_id
            ),
            "RecurringOrder",
        )
        ensure_related_to_shop(current_user, recurring_order.shop_id)

        weekdays, month_days = normalize_schedule(
            schedule_type=command.schedule_type,
            weekdays=command.weekdays,
            month_days=command.month_days,
        )
        validate_items(
            len(command.items), [item.quantity for item in command.items]
        )

        client = ensure_exists(
            await self._client_gateway.load(recurring_order.client_id),
            "Client",
        )
        ensure_related_to_shop(current_user, client.shop_id)
        if not any(
            address.id == command.address_id for address in client.addresses
        ):
            entity = "Address"
            raise EntityNotFoundError(entity, command.address_id)
        if not any(phone.id == command.phone_id for phone in client.phones):
            entity = "Phone"
            raise EntityNotFoundError(entity, command.phone_id)

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(command.time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)

        if not await self._payment_method_gateway.exists_by_name_in_shop(
            current_user.shop_id, command.payment_method
        ):
            entity = "PaymentMethod"
            raise EntityNotFoundError(entity)

        products = await self._product_gateway.load_many([
            item.product_id for item in command.items
        ])
        products_by_id = {product.id: product for product in products}
        for item in command.items:
            product = ensure_exists(
                products_by_id.get(item.product_id), "Product"
            )
            if product.shop_id != current_user.shop_id:
                raise AccessDeniedError

        recurring_order.address_id = command.address_id
        recurring_order.phone_id = command.phone_id
        recurring_order.time_slot_id = command.time_slot_id
        recurring_order.payment_method = command.payment_method
        recurring_order.comment = command.comment
        recurring_order.schedule_type = command.schedule_type
        recurring_order.weekdays = weekdays
        recurring_order.month_days = month_days
        recurring_order.items = [
            RecurringOrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
            )
            for item in command.items
        ]

        await self._tr_manager.commit()
        logger.info("Recurring order %s updated", recurring_order.id)
