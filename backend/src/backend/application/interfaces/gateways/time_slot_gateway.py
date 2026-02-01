from dataclasses import dataclass

from backend.application.vars import TimeSlotId


@dataclass(frozen=True)
class TimeSlotReadModel:
    time_slot_id: TimeSlotId
    start_time: str
    end_time: str
    label: str | None
