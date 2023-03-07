from pathlib import Path
from typing import Optional

from ted_sws.core.model import PropertyBaseModel


class ReportNoticeData(PropertyBaseModel):
    """
    Used for storing
    """
    notice_id: str
    path: Optional[str]
