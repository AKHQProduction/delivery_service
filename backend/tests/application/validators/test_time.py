from datetime import time

import pytest

from backend.application.errors import InvalidTimeSlotRangeError
from backend.application.validators.time import validate_time_slot_range


class TestValidateTimeSlotRange:
    def test_valid_range(self):
        validate_time_slot_range(time(9, 0), time(17, 0))
        validate_time_slot_range(time(0, 0), time(23, 59))
        validate_time_slot_range(time(12, 30), time(13, 0))

    def test_invalid_range_end_before_start(self):
        with pytest.raises(InvalidTimeSlotRangeError) as exc_info:
            validate_time_slot_range(time(17, 0), time(9, 0))
        assert (
            "end_time must be greater than start_time"
            in exc_info.value.message
        )

    def test_invalid_range_equal_times(self):
        with pytest.raises(InvalidTimeSlotRangeError) as exc_info:
            validate_time_slot_range(time(12, 0), time(12, 0))
        assert (
            "end_time must be greater than start_time"
            in exc_info.value.message
        )
