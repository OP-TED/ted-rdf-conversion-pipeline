import abc
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Type, Union

from pymongo import MongoClient

from ted_sws import config
from ted_sws.event_manager.adapters.event_handler import EventHandler, EventWriterToConsoleHandler, \
    EventWriterToFileHandler, EventWriterToNullHandler, EventWriterToMongoDBHandler
from ted_sws.event_manager.adapters.log import ConfigHandlerType

NOW = datetime.now(timezone.utc)
DEFAULT_LOGGER_NAME = "ROOT"
DEFAULT_NULL_LOGGER_NAME = "NULL"
DEFAULT_CONSOLE_LOGGER_NAME = "CONSOLE"
DEFAULT_LOGGER_LOG_FILENAME = "./event_logs/{today}.log"  # EXAMPLE: ./event_logs/{today}/{hour}/{minute}.log"
CONFIG_HANDLERS_SEP = ","

HANDLERS_TYPE = List[EventHandler]
EVENT_HANDLER_TYPE = Union[
    EventHandler, EventWriterToConsoleHandler, EventWriterToMongoDBHandler, EventWriterToFileHandler
]

"""
This module contains the event handler configurations' adapters to be used by event loggers.
"""


class EventHandlerConfigABC(abc.ABC):
    """
    This abstract class contains the definitions of main event handler config methods.
    """

    @abc.abstractmethod
    def get_handlers(self) -> HANDLERS_TYPE:
        """This method returns default environment handlers"""


class EventHandlerConfig(EventHandlerConfigABC):
    """
    This is the base event handler config class.
    """
    handlers: HANDLERS_TYPE = None
    prime_handlers: HANDLERS_TYPE = None

    def __init__(self, handlers: HANDLERS_TYPE = None, prime_handlers: HANDLERS_TYPE = None):
        """
        This is the constructor/initialization of base event handler config.

        :param handlers: default environment handlers
        :param prime_handlers: all supported handlers
        """
        self.handlers = handlers
        self.prime_handlers = prime_handlers

    def get_handlers(self) -> HANDLERS_TYPE:
        """
        This method return default environment handlers for current config.

        :return: A list of event handlers
        """
        return self.handlers

    def get_prime_handlers(self) -> HANDLERS_TYPE:
        """
        This method return all supported handlers for current config.

        :return: A list of event handlers
        """
        return self.prime_handlers

    @classmethod
    def init_log_filepath(cls, filepath: Path = None) -> Path:
        """
        This method initializes the output filepath for file handlers.

        :param filepath: The provided filepath
        :return: The filepath to be used
        """
        if filepath is None:
            config_filename = config.LOGGER_LOG_FILENAME
            filename = config_filename if config_filename else DEFAULT_LOGGER_LOG_FILENAME

            filepath = Path(filename.format(
                today=NOW.strftime('%Y-%m-%d'),
                hour=NOW.strftime('%Y-%m-%d_%H'),
                minute=NOW.strftime('%Y-%m-%d_%H-%M')
            ))
        return filepath

    @classmethod
    def init_logger_name(cls, name: str = None) -> str:
        """
        This method initializes the logger name.

        :param name: The provided logger name
        :return: The logger name to be used
        """
        return name if name else DEFAULT_LOGGER_NAME

    def _init_handlers(self, config_handlers, default_handlers: HANDLERS_TYPE, handlers: HANDLERS_TYPE,
                       mongodb_client: MongoClient, name: str, filepath: Path) -> (HANDLERS_TYPE, HANDLERS_TYPE):
        """
        This method initializes the default environment and all supported event handlers.

        :param config_handlers: Environment config event handlers
        :param default_handlers: Default event handlers
        :param handlers: Forced event handlers
        :param mongodb_client: MongoDB client
        :param name: Default/base event handlers' name
        :param filepath: The output filepath
        :return: None
        """
        name = self.init_logger_name(name)
        filepath = self.init_log_filepath(filepath)

        console_handler: EventWriterToConsoleHandler = EventWriterToConsoleHandler(name=name)
        mongodb_handler: EventWriterToMongoDBHandler = EventWriterToMongoDBHandler(mongodb_client=mongodb_client)
        file_handler: EventWriterToFileHandler = EventWriterToFileHandler(filepath=filepath, name=name)

        prime_handlers: HANDLERS_TYPE = [console_handler, mongodb_handler, file_handler]

        if not handlers:
            if config_handlers:
                handlers: HANDLERS_TYPE = []
                config_handlers = config_handlers.split(CONFIG_HANDLERS_SEP)
                if ConfigHandlerType.ConsoleHandler.value in config_handlers:
                    handlers.append(console_handler)
                if ConfigHandlerType.MongoDBHandler.value in config_handlers:
                    handlers.append(mongodb_handler)
                if ConfigHandlerType.FileHandler.value in config_handlers:
                    handlers.append(file_handler)
            else:
                handlers = default_handlers
        return handlers, prime_handlers

    def get_handler(self, handler_type: Type[EventHandler]) -> EVENT_HANDLER_TYPE:
        """
        Used to retrieve the event handler from environment handlers, by event handler class type.

        :param handler_type: Event handler class type
        :return: Event handler or None
        """
        return next(filter(lambda handler: isinstance(handler, handler_type), self.handlers), None)

    def get_console_handler(self) -> EventWriterToConsoleHandler:
        """
        Used to retrieve the console event handler from environment handlers.

        :return: The console event handler or None
        """
        return self.get_handler(EventWriterToConsoleHandler)


class DAGLoggerConfig(EventHandlerConfig):
    """
    This is the event handler config class for DAG event message logging.
    """

    def __init__(self, mongodb_client: MongoClient = None, name: str = DEFAULT_LOGGER_NAME, filepath: Path = None,
                 handlers: HANDLERS_TYPE = None, config_handlers: str = None):
        """
        This is the constructor/initialization of DAG event handler config.

        :param mongodb_client: The MongoDB client
        :param name: Base event handlers' name
        :param filepath: The output filepath
        :param handlers: Forced event handlers
        :param config_handlers: Environment config event handlers for DAG
        """
        config_handlers = config_handlers if config_handlers else config.DAG_LOGGER_CONFIG_HANDLERS
        handlers, prime_handlers = self._init_handlers(
            config_handlers=config_handlers,
            default_handlers=[
                EventWriterToConsoleHandler(name=name),
                EventWriterToMongoDBHandler(mongodb_client=mongodb_client)
            ],
            handlers=handlers,
            mongodb_client=mongodb_client,
            name=name,
            filepath=filepath
        )
        super().__init__(handlers, prime_handlers)


class CLILoggerConfig(EventHandlerConfig):
    """
    This is the event handler config class for CLI event message logging.
    """

    def __init__(self, mongodb_client: MongoClient = None, name: str = DEFAULT_LOGGER_NAME, filepath: Path = None,
                 handlers: HANDLERS_TYPE = None, config_handlers: str = None):
        """
        This is the constructor/initialization of CLI event handler config.

        :param mongodb_client: The MongoDB client
        :param name: Base event handlers' name
        :param filepath: The output filepath
        :param handlers: Forced event handlers
        :param config_handlers: Environment config event handlers for CLI
        """
        config_handlers = config_handlers if config_handlers else config.CLI_LOGGER_CONFIG_HANDLERS
        handlers, prime_handlers = self._init_handlers(
            config_handlers=config_handlers,
            default_handlers=[
                EventWriterToConsoleHandler(name=name)
            ],
            handlers=handlers,
            mongodb_client=mongodb_client,
            name=name,
            filepath=filepath
        )
        super().__init__(handlers, prime_handlers)


class NullLoggerConfig(EventHandlerConfig):
    """
    This is the event handler config class for NULL event message logging.
    """

    def __init__(self, name: str = DEFAULT_NULL_LOGGER_NAME):
        """
        This is the constructor/initialization of NULL event handler config.

        :param name: Base event handler's name
        """
        null_handler: EventWriterToNullHandler = EventWriterToNullHandler(name=name)
        handlers = [null_handler]
        super().__init__(handlers, handlers)


class ConsoleLoggerConfig(EventHandlerConfig):
    """
    This is the event handler config class for Console event message logging.
    """

    def __init__(self, name: str = DEFAULT_CONSOLE_LOGGER_NAME):
        """
        This is the constructor/initialization of Console event handler config.

        :param name: Base event handler's name
        """
        console_handler: EventWriterToConsoleHandler = EventWriterToConsoleHandler(name=name)
        handlers = [console_handler]
        super().__init__(handlers, handlers)
