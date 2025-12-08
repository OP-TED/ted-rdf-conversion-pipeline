from typing import Optional

from ted_sws.core.model import PropertyBaseModel


class ReportNoticeData(PropertyBaseModel):
    """
    Used for storing
    """
    notice_id: str
    path: Optional[str]


class ReportPackageNoticeData(ReportNoticeData):
    """
    Used for storing
    """
    mapping_suite_versioned_id: Optional[str]
    mapping_suite_identifier: Optional[str]
