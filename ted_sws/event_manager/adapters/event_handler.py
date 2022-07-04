import abc
import logging
import sys
from pathlib import Path

from ted_sws.event_manager.adapters.event_logging_repository import EventLoggingRepository
from ted_sws.event_manager.model.event_message import EventMessage, SeverityLevelType


class EventHandlerABC(abc.ABC):
    @abc.abstractmethod
    def log(self, severity_level: SeverityLevelType, event_message: EventMessage):
        pass


class EventHandler(EventHandlerABC):
    def log(self, severity_level: SeverityLevelType, event_message: EventMessage):
        pass


class EventWriterToStdoutHandler(EventHandler):
    logger: logging.Logger

    def __init__(self, name: str):
        console = logging.StreamHandler(sys.stdout)
        self.logger = logging.getLogger(name)
        self.logger.handlers.clear()
        self.logger.addHandler(console)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage):
        self.logger.log(severity_level.value, event_message.message)


class EventWriterToFileHandler(EventHandler):
    logger: logging.Logger

    def __init__(self, filepath: Path):
        file_handler = logging.FileHandler(filepath)
        self.logger = logging.getLogger(__name__)
        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage):
        self.logger.log(severity_level.value, event_message.message)


class EventWriterToMongoDBHandler(EventHandler):
    repository: EventLoggingRepository

    def __init__(self, event_logging_repository: EventLoggingRepository):
        self.repository = event_logging_repository

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage):
        event_message.severity_level = severity_level.value
        self.repository.add(event_message)
