from datetime import time

from pydantic import BaseModel


class SlotCreateRequest(BaseModel):
    slot_start_time: time
    slot_end_time: time


class SlotResponse(BaseModel):
    slot_id: int
    slot_start_time: time
    slot_end_time: time
