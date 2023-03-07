from pathlib import Path
from typing import Optional

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.notice import Notice


class ReportNoticeMetadata(PropertyBaseModel):
    path: Optional[Path]


class ReportNotice(PropertyBaseModel):
    """
    Used for processing
    """
    notice: Notice
    metadata: Optional[ReportNoticeMetadata] = ReportNoticeMetadata()


