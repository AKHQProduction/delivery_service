from dataclasses import dataclass
from datetime import time
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping


class AvailableTimeSlot(str, Enum):
    MORNING = "MORNING"
    MIDDAY = "MIDDAY"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"


SELECTED_TIME_SLOT: Final[Mapping[AvailableTimeSlot, tuple[time, time]]] = (
    MappingProxyType(
        {
            AvailableTimeSlot.MORNING: (time(hour=9), time(hour=12)),
            AvailableTimeSlot.MIDDAY: (time(12), time(15)),
            AvailableTimeSlot.AFTERNOON: (time(15), time(18)),
            AvailableTimeSlot.EVENING: (time(18), time(21)),
        }
    )
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class TimeSlot:
    start_time: time
    end_time: time

    @staticmethod
    def set_slot(selected_slot: AvailableTimeSlot) -> "TimeSlot":
        start_time, end_time = SELECTED_TIME_SLOT[selected_slot]

        return TimeSlot(start_time=start_time, end_time=end_time)
