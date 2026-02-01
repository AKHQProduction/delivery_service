from dataclasses import dataclass
from datetime import time

from backend.application.vars import ShopId, TimeSlotId


@dataclass
class TimeSlot:
    time_slot_id: TimeSlotId
    shop_id: ShopId
    start_time: time
    end_time: time
    label: str | None


@dataclass(frozen=True)
class CreateTimeSlotDTO:
    time_slot_id: TimeSlotId
    shop_id: ShopId
    start_time: time
    end_time: time
    label: str | None


@dataclass(frozen=True)
class TimeSlotReadModel:
    time_slot_id: TimeSlotId
    start_time: str
    end_time: str
    label: str | None
