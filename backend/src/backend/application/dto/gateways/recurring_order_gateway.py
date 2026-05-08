from dataclasses import dataclass

from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    ProductId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    TimeSlotId,
)


@dataclass(frozen=True)
class RecurringOrderFilters:
    client_name: str | None = None
    status: RecurringOrderStatus | None = None
    schedule_type: ScheduleType | None = None
    weekday: int | None = None
    month_day: int | None = None


@dataclass(frozen=True)
class RecurringOrderReadModel:
    recurring_order_id: RecurringOrderId
    client_id: ClientId
    client_name: str
    phone_id: PhoneId | None
    phone_number: str | None
    address_id: AddressId | None
    address_summary: str | None
    time_slot_id: TimeSlotId
    time_slot_label: str | None
    delivery_start_time: str
    delivery_end_time: str
    schedule_type: ScheduleType
    weekdays: list[int] | None
    month_days: list[int] | None
    items_count: int
    status: RecurringOrderStatus


@dataclass(frozen=True)
class RecurringOrderItemReadModel:
    product_id: ProductId
    product_name: str
    quantity: int
    current_price: int


@dataclass(frozen=True)
class RecurringOrderDetailReadModel(RecurringOrderReadModel):
    payment_method: str
    comment: str | None
    items: list[RecurringOrderItemReadModel]
