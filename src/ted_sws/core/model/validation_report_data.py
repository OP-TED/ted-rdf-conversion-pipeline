from typing import Optional

from src.ted_sws.core.model import PropertyBaseModel


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
    mapping_package_versioned_id: Optional[str]
    mapping_package_identifier: Optional[str]
