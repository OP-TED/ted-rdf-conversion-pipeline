from enum import Enum
from typing import Optional
import logging
from datetime import datetime, timezone
from ted_sws.core.model import PropertyBaseModel


class SeverityLevelType(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class EventMessage(PropertyBaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)
    year: datetime = datetime.now(timezone.utc).year
    month: datetime = datetime.now(timezone.utc).month
    day: datetime = datetime.now(timezone.utc).day
    severity_level: Optional[SeverityLevelType] = None
    caller_name: Optional[str] = None
    duration: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True


class TechnicalEventMessage(EventMessage):
    pass


class NoticeEventMessage(EventMessage):
    notice_id: Optional[str] = None
    domain_action: Optional[str] = None


class MappingSuiteEventMessage(EventMessage):
    mapping_suite_id: Optional[str] = None
