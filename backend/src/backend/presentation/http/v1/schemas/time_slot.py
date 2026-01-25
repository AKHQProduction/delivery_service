from datetime import time

from pydantic import BaseModel


class EditTimeSlotSchema(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    label: str | None = None
