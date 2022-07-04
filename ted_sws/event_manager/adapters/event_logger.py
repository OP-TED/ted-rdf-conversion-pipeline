from ted_sws.event_manager.model.event_message import SeverityLevelType
from ted_sws.event_manager.adapters.event_logging_repository import EventMessageType, EventLoggingRepository
import logging
import abc
from pathlib import Path
from typing import Union


class EventHandlerConfigABC(abc.ABC):
    @abc.abstractmethod
    def log(self, severity_level: SeverityLevelType, event_message: Union[EventMessageType, str]):
        pass


class DAGLoggerConfig(EventHandlerConfigABC):
    def __init__(self, event_logging_repository: EventLoggingRepository):
        self.repository = event_logging_repository

    def log(self, severity_level: SeverityLevelType, event_message: EventMessageType):
        event_message.severity_level = severity_level.value
        self.repository.add(event_message)


class CLILoggerConfig(EventHandlerConfigABC):
    def __init__(self, filepath: Path):
        handler = logging.FileHandler(filepath)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)

    def log(self, severity_level: SeverityLevelType, message: str):
        self.logger.log(severity_level.value, message)
        pass


class EventLogger:
    event_handler: EventHandlerConfigABC

    def __init__(self, event_handler: EventHandlerConfigABC):
        self.event_handler = event_handler
        pass

    def debug(self, event_message: EventMessageType):
        self.event_handler.log(SeverityLevelType.DEBUG, event_message)

    def info(self, event_message: EventMessageType):
        self.event_handler.log(SeverityLevelType.INFO, event_message)

    def warning(self, event_message: EventMessageType):
        self.event_handler.log(SeverityLevelType.WARNING, event_message)

    def error(self, event_message: EventMessageType):
        self.event_handler.log(SeverityLevelType.ERROR, event_message)


