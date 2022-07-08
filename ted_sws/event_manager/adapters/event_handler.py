import abc
import inspect
import logging
import sys
from pathlib import Path

from pymongo import MongoClient

from ted_sws.event_manager.adapters.event_logging_repository import EventLoggingRepository, TechnicalEventRepository, \
    NoticeEventRepository, MappingSuiteEventRepository
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.model.event_message import EventMessage, SeverityLevelType, TechnicalEventMessage, \
    NoticeEventMessage, MappingSuiteEventMessage, EventMessageLogSettings

DEFAULT_LOGGER_LOG_FORMAT = "[%(asctime)s] - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOGGER_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_SEVERITY_LEVEL = SeverityLevelType.DEBUG


class EventHandlerABC(abc.ABC):
    @abc.abstractmethod
    def log(self, severity_level: SeverityLevelType, event_message: EventMessage, settings: EventMessageLogSettings):
        """This method logs EventMessage"""


class EventHandler(EventHandlerABC):
    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        pass

    @classmethod
    def _caller_name(cls, event_message: EventMessage) -> str:
        caller_name = event_message.caller_name
        if not caller_name:
            caller_name = inspect.stack()[5][3]
        return caller_name


class EventLoggingHandler(EventHandler):
    logger: logging.Logger

    def init_handler(self, handler, name: str, fmt: str = None,
                     severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL,
                     handler_type: ConfigHandlerType = None):
        logger_name = (handler_type.value + ':' if handler_type else '') + name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(severity_level.value)

        handler.setLevel(severity_level.value)
        if fmt is None:
            fmt = DEFAULT_LOGGER_LOG_FORMAT
        date_fmt = DEFAULT_LOGGER_LOG_DATE_FORMAT
        formatter = logging.Formatter(fmt, date_fmt)
        handler.setFormatter(formatter)

        self.logger.handlers.clear()
        self.logger.addHandler(handler)

    @classmethod
    def _prepare_message(cls, event_message: EventMessage):
        event_message.caller_name = cls._caller_name(event_message)
        return str(event_message.dict())

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        if settings.briefly:
            message = (event_message.title + ': ' if event_message.title else '') + event_message.message
        else:
            event_message.severity_level = severity_level
            message = self._prepare_message(event_message)
        message = event_message.__class__.__name__ + " :: " + message
        self.logger.log(severity_level.value, message)


class EventWriterToConsoleHandler(EventLoggingHandler):
    name: str

    def __init__(self, name: str, fmt: str = None,
                 severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL):
        self.name = name
        self.init_handler(logging.StreamHandler(sys.stdout), name, fmt, severity_level,
                          ConfigHandlerType.ConsoleHandler)
        self.logger.propagate = False


class EventWriterToFileHandler(EventLoggingHandler):
    filepath: Path
    filepath_created: bool = False

    def __init__(self, filepath: Path, name: str = None, fmt: str = None,
                 severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL):
        self.filepath = filepath
        if name is None:
            name = __name__
        self.init_handler(logging.FileHandler(filepath, delay=True), name, fmt, severity_level,
                          ConfigHandlerType.FileHandler)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        if not self.filepath_created:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.filepath_created = True
        super().log(severity_level, event_message, settings)


class EventWriterToNullHandler(EventLoggingHandler):
    name: str

    def __init__(self, name: str):
        self.name = name
        self.init_handler(logging.NullHandler(), name)


class EventWriterToMongoDBHandler(EventHandler):
    mongodb_client: MongoClient

    def __init__(self, mongodb_client: MongoClient):
        self.mongodb_client = mongodb_client

    def get_repository_for_event_message(self, event_message: EventMessage) -> EventLoggingRepository:
        if isinstance(event_message, TechnicalEventMessage):
            return TechnicalEventRepository(mongodb_client=self.mongodb_client)
        elif isinstance(event_message, NoticeEventMessage):
            return NoticeEventRepository(mongodb_client=self.mongodb_client)
        elif isinstance(event_message, MappingSuiteEventMessage):
            return MappingSuiteEventRepository(mongodb_client=self.mongodb_client)
        return EventLoggingRepository(mongodb_client=self.mongodb_client)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        repository: EventLoggingRepository = self.get_repository_for_event_message(event_message)
        event_message.severity_level = severity_level.value
        event_message.caller_name = self._caller_name(event_message)
        result = repository.add(event_message)
        return result
