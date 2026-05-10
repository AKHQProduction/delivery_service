from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.services.recurring.template import (
    normalize_schedule,
    validate_items,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    ProductId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    TimeSlotId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyPaymentMethodGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
)


@dataclass(frozen=True)
class RecurringOrderProductInput:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class RecurringOrderTemplateDraft:
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


class RecurringOrderTemplateWritePolicy:
    def __init__(
        self,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
    ) -> None:
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._time_slot_gateway = time_slot_gateway
        self._payment_method_gateway = payment_method_gateway

    async def create(
        self,
        *,
        recurring_order_id: RecurringOrderId,
        shop_id: ShopId,
        draft: RecurringOrderTemplateDraft,
    ) -> RecurringOrder:
        recurring_order = RecurringOrder(
            id=recurring_order_id,
            shop_id=shop_id,
            client_id=draft.client_id,
            address_id=draft.address_id,
            phone_id=draft.phone_id,
            time_slot_id=draft.time_slot_id,
            payment_method=draft.payment_method,
            comment=draft.comment,
            schedule_type=draft.schedule_type,
            weekdays=[],
            month_days=None,
            status=RecurringOrderStatus.ACTIVE,
        )
        await self.apply(recurring_order, shop_id=shop_id, draft=draft)
        return recurring_order

    async def apply(
        self,
        recurring_order: RecurringOrder,
        *,
        shop_id: ShopId,
        draft: RecurringOrderTemplateDraft,
    ) -> None:
        weekdays, month_days = await self._validate(shop_id, draft)

        recurring_order.client_id = draft.client_id
        recurring_order.address_id = draft.address_id
        recurring_order.phone_id = draft.phone_id
        recurring_order.time_slot_id = draft.time_slot_id
        recurring_order.payment_method = draft.payment_method
        recurring_order.comment = draft.comment
        recurring_order.schedule_type = draft.schedule_type
        recurring_order.weekdays = weekdays
        recurring_order.month_days = month_days
        recurring_order.items = [
            RecurringOrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
            )
            for item in draft.items
        ]

    async def _validate(
        self,
        shop_id: ShopId,
        draft: RecurringOrderTemplateDraft,
    ) -> tuple[list[int] | None, list[int] | None]:
        weekdays, month_days = normalize_schedule(
            schedule_type=draft.schedule_type,
            weekdays=draft.weekdays,
            month_days=draft.month_days,
        )
        validate_items(
            len(draft.items), [item.quantity for item in draft.items]
        )

        client = ensure_exists(
            await self._client_gateway.load(draft.client_id), "Client"
        )
        if client.shop_id != shop_id:
            raise AccessDeniedError
        has_address = any(
            address.id == draft.address_id for address in client.addresses
        )
        if not has_address:
            entity = "Address"
            raise EntityNotFoundError(entity, draft.address_id)
        if not any(phone.id == draft.phone_id for phone in client.phones):
            entity = "Phone"
            raise EntityNotFoundError(entity, draft.phone_id)

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(draft.time_slot_id),
            "TimeSlot",
        )
        if time_slot.shop_id != shop_id:
            raise AccessDeniedError

        if not await self._payment_method_gateway.exists_by_name_in_shop(
            shop_id, draft.payment_method
        ):
            entity = "PaymentMethod"
            raise EntityNotFoundError(entity)

        products = await self._product_gateway.load_many([
            item.product_id for item in draft.items
        ])
        products_by_id = {product.id: product for product in products}
        for item in draft.items:
            product = ensure_exists(
                products_by_id.get(item.product_id), "Product"
            )
            if product.shop_id != shop_id:
                raise AccessDeniedError

        return weekdays, month_days
