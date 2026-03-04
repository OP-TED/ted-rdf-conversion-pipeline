from typing import List

from pydantic import BaseModel, Field

from src.ted_sws.core.model.notice import NoticeStatus


class NoticeStatusBatch(BaseModel):
    notice_status: NoticeStatus = Field(..., description="Status of the notices in this batch")
    notice_ids: List[str] = Field(..., description="List of notice IDs belonging to this status")
    start_with_step_name: str = Field(..., description="Pipeline step to start processing from")

    model_config = {
        "frozen": True
    }
