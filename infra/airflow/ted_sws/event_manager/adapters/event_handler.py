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

"""
This module contains the event handler adapters for logging event messages by event loggers.
"""


class EventHandlerABC(abc.ABC):
    """
    This abstract class contains the definitions of main event handler methods.
    """

    @abc.abstractmethod
    def log(self, severity_level: SeverityLevelType, event_message: EventMessage, settings: EventMessageLogSettings):
        """
        This is the skeleton for method that logs an event message.

        :param severity_level: The severity level of event_message
        :param event_message: The event message to be logged
        :param settings: Settings to adjust the event message logging process
        :return: None
        """


class EventHandler(EventHandlerABC):
    """
    This is the base event handler class.
    """

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        This is the base/default method that logs event message.

        :param severity_level: The logging severity level
        :param event_message: The event message to be logged
        :param settings: The logging settings
        :return: None
        """
        pass

    @classmethod
    def _caller_name(cls, event_message: EventMessage) -> str:
        """
        This method returns/guesses the event message caller name.

        :param event_message: The event message
        :return: A string that represents the event message caller name
        """
        caller_name = event_message.caller_name
        if not caller_name:
            caller_name = inspect.stack()[5][3]
        return caller_name


class EventLoggingHandler(EventHandler):
    """
    This is the base class for event handlers that use Python logging module handlers.
    """
    logger: logging.Logger

    def init_handler(self, handler, name: str, fmt: str = None,
                     severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL,
                     handler_type: ConfigHandlerType = None):
        """
        This method performs the base logging handler initialization.

        :param handler: The logging handler
        :param name: The handler's name (used as a unique key)
        :param fmt: The log format string
        :param severity_level: The logging severity level
        :param handler_type: The config handler type (used to separate Python loggers)
        :return: None
        """
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

        self.logger.propagate = False

    @classmethod
    def _prepare_message(cls, event_message: EventMessage):
        """
        This method prepare the EventMessage object to be loggable by logging handler.

        :param event_message: The event message object
        :return: None
        """
        event_message.caller_name = cls._caller_name(event_message)
        return str(event_message.dict())

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        In this method the logger logs the event message to logging handler's output.

        :param severity_level: The log severity level
        :param event_message: The event message to be logged
        :param settings: The logging settings
        :return: None
        """
        if settings.briefly:
            message = event_message.message
        else:
            event_message.severity_level = severity_level
            message = self._prepare_message(event_message)
        message = event_message.__class__.__name__ + " :: " + message
        self.logger.log(severity_level.value, message)


class EventWriterToConsoleHandler(EventLoggingHandler):
    """
    This is the class for console/stdout logging handler.
    """
    name: str

    def __init__(self, name: str, fmt: str = None,
                 severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL):
        """
        This is the constructor/initialization of console logging handler.

        :param name: The logging handler/logger's name
        :param fmt: The logging format string
        :param severity_level: The logging severity level
        """
        self.name = name
        self.init_handler(logging.StreamHandler(sys.stdout), name, fmt, severity_level,
                          ConfigHandlerType.ConsoleHandler)


class EventWriterToFileHandler(EventLoggingHandler):
    """
    This is the class for file logging handler.
    """
    filepath: Path
    filepath_created: bool = False

    def __init__(self, filepath: Path, name: str = None, fmt: str = None,
                 severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL):
        """
        This is the constructor/initialization of file logging handler.
        The FileHandler must be initialized with delay=True to avoid file creation before logging is performed.

        :param filepath: The path to the output file
        :param name: The logging handler/logger's name
        :param fmt: The logging format string
        :param severity_level: The logging severity level
        """
        self.filepath = filepath
        if name is None:
            name = __name__
        self.init_handler(logging.FileHandler(filepath, delay=True), name, fmt, severity_level,
                          ConfigHandlerType.FileHandler)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        This method logs the event message to provided file.
        The output file is created, if it's the first log.
        The instance property filepath_created is used to check the existence of the file, to avoid performance issues.

        :param severity_level: The logging severity level
        :param event_message: The event message to be logged
        :param settings: The logging settings
        :return:
        """
        if not self.filepath_created:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.filepath_created = True
        super().log(severity_level, event_message, settings)


class EventWriterToNullHandler(EventLoggingHandler):
    """
    This is the class for null logging handler. It's here for testing purposes.
    It is used in test environment to avoid unneeded logging, without making the logging exclusion.
    """
    name: str

    def __init__(self, name: str):
        """
        This is the constructor/initialization of null logging handler.

        :param name: The logging handler/logger's name
        """
        self.name = name
        self.init_handler(logging.NullHandler(), name)


class EventWriterToMongoDBHandler(EventHandler):
    """
    This is the class for MongoDB logging handler.
    """
    mongodb_client: MongoClient

    def __init__(self, mongodb_client: MongoClient):
        """
        This is the constructor/initialization of MongoDB logging handler.

        :param mongodb_client: The MongoDB client to be used
        """
        self.mongodb_client = mongodb_client

    def get_repository_for_event_message(self, event_message: EventMessage) -> EventLoggingRepository:
        """
        This method returns MongoDB/event repository(collection handler) based on event message type to be logged.

        :param event_message: The event message to be logged.
        :return: The event logging repository the event message will be logged in
        """
        if isinstance(event_message, TechnicalEventMessage):
            return TechnicalEventRepository(mongodb_client=self.mongodb_client)
        elif isinstance(event_message, NoticeEventMessage):
            return NoticeEventRepository(mongodb_client=self.mongodb_client)
        elif isinstance(event_message, MappingSuiteEventMessage):
            return MappingSuiteEventRepository(mongodb_client=self.mongodb_client)
        return EventLoggingRepository(mongodb_client=self.mongodb_client)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage,
            settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        This method logs the event message to MongoDB collection, based on event message type.

        :param severity_level: The logging severity level
        :param event_message: The event message to be logged
        :param settings: The logging settings
        :return: None
        """
        repository: EventLoggingRepository = self.get_repository_for_event_message(event_message)
        event_message.severity_level = severity_level.value
        event_message.caller_name = self._caller_name(event_message)
        result = repository.add(event_message)
        return result
