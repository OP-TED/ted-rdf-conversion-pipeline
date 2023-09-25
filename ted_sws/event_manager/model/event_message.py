from datetime import datetime
from enum import Enum
from typing import Optional, Union, Dict, Any

from pydantic import Field

from ted_sws.core.model import PropertyBaseModel, BaseModel
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.event_manager.adapters.log import SeverityLevelType

DictType = Union[Dict[str, Any], None]

"""
This module contains event message related models.
"""


class EventMessageProcessType(str, Enum):
    """
    Event message process type.
    """
    DAG = 'DAG'
    CLI = 'CLI'


class EventMessageMetadata(BaseModel):
    """
    This is the event message metadata.
    """
    process_type: Optional[EventMessageProcessType] = None
    process_name: Optional[str] = None
    process_id: Optional[str] = None
    process_context: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class EventMessage(PropertyBaseModel):
    """
    This is the event message model.
    """
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    severity_level: Optional[SeverityLevelType] = None
    caller_name: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[float] = None
    metadata: Optional[EventMessageMetadata] = None
    kwargs: Optional[DictType] = None

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    def __init__(self, **data):
        """
        This is the event message initialization (on object instance creation).
        
        :param data: The input data
        """
        super().__init__(**data)
        self.create()

    def create(self):
        """
        This method is called when event message object is instantiated.

        :return: None
        """
        self.created_at = datetime.utcnow()
        self.year = self.created_at.year
        self.month = self.created_at.month
        self.day = self.created_at.day

    def start_record(self):
        """
        This method should be called when the event message record is intended to start.
        Event message updates related to record's start are handled here.

        :return: None
        """
        self.started_at = datetime.utcnow()

    def end_record(self):
        """
        This method should be called when the event message record is intended to end.
        Event message updates related to record's end are handled here.

        :return: None
        """
        self.ended_at = datetime.utcnow()
        self.duration = (self.ended_at - self.started_at).total_seconds()


class TechnicalEventMessage(EventMessage):
    """
    This is the technical event message model.
    """
    pass


class NoticeEventMessage(EventMessage):
    """
    This is the notice event message model.
    """
    notice_id: Optional[str] = None
    domain_action: Optional[str] = None
    notice_form_number: Optional[str] = None
    notice_eforms_subtype: Optional[str] = None
    notice_status: Optional[NoticeStatus] = None


class MappingSuiteEventMessage(EventMessage):
    """
    This is the mapping suite event message model.
    """
    mapping_suite_id: Optional[str] = None


class EventMessageLogSettings(PropertyBaseModel):
    """
    This is the event message logging settings model.
    """
    briefly: Optional[bool] = False
    force_handlers: Optional[bool] = False
