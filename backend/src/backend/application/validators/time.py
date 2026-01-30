from datetime import time

from backend.application.errors import InvalidTimeSlotRangeError


def validate_time_slot_range(start_time: time, end_time: time) -> None:
    if end_time <= start_time:
        raise InvalidTimeSlotRangeError
