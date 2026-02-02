from datetime import time

from backend.application.vars import ShopId, TimeSlotId
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)


def create_time_slot(
    *,
    time_slot_id: TimeSlotId,
    shop_id: ShopId,
    start_time: time,
    end_time: time,
    label: str | None,
) -> ShopDeliveryTimeSlot:
    return ShopDeliveryTimeSlot(
        id=time_slot_id,
        shop_id=shop_id,
        start_time=start_time,
        end_time=end_time,
        label=label,
    )


def update_time_slot(
    time_slot: ShopDeliveryTimeSlot,
    *,
    start_time: time | None = None,
    end_time: time | None = None,
    label: str | None = None,
) -> None:
    if start_time is not None:
        time_slot.start_time = start_time
    if end_time is not None:
        time_slot.end_time = end_time
    if label is not None:
        time_slot.label = label
