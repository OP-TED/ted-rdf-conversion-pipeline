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
DEFAULT_LOGGER_LOG_FILENAME = "./event_logs/{today}.log"
# DEFAULT_LOGGER_LOG_FILENAME = "./event_logs/{today}/{hour}/{minute}.log" # EXAMPLE
CONFIG_HANDLERS_SEP = ","

HANDLERS_TYPE = List[EventHandler]
EVENT_HANDLER_TYPE = Union[
    EventHandler, EventWriterToConsoleHandler, EventWriterToMongoDBHandler, EventWriterToConsoleHandler
]


class EventHandlerConfigABC(abc.ABC):
    @abc.abstractmethod
    def get_handlers(self) -> HANDLERS_TYPE:
        """This method returns active Config Handlers"""


class EventHandlerConfig(EventHandlerConfigABC):
    handlers: HANDLERS_TYPE = None
    prime_handlers: HANDLERS_TYPE = None

    def __init__(self, handlers: HANDLERS_TYPE = None, prime_handlers: HANDLERS_TYPE = None):
        self.handlers = handlers
        self.prime_handlers = prime_handlers

    def get_handlers(self) -> HANDLERS_TYPE:
        return self.handlers

    def get_prime_handlers(self) -> HANDLERS_TYPE:
        return self.prime_handlers

    @classmethod
    def init_log_filepath(cls, filepath: Path = None) -> Path:
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
        return name if name else DEFAULT_LOGGER_NAME

    def _init_handlers(self, config_handlers, default_handlers: HANDLERS_TYPE, handlers: HANDLERS_TYPE,
                       mongodb_client: MongoClient, name: str, filepath: Path) -> (HANDLERS_TYPE, HANDLERS_TYPE):
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
        return next(filter(lambda handler: isinstance(handler, handler_type), self.handlers), None)

    def get_console_handler(self) -> EventWriterToConsoleHandler:
        return self.get_handler(EventWriterToConsoleHandler)


class DAGLoggerConfig(EventHandlerConfig):
    def __init__(self, mongodb_client: MongoClient = None, name: str = DEFAULT_LOGGER_NAME, filepath: Path = None,
                 handlers: HANDLERS_TYPE = None, config_handlers: str = config.DAG_LOGGER_CONFIG_HANDLERS):
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
    def __init__(self, mongodb_client: MongoClient = None, name: str = DEFAULT_LOGGER_NAME, filepath: Path = None,
                 handlers: HANDLERS_TYPE = None, config_handlers: str = config.CLI_LOGGER_CONFIG_HANDLERS):
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


class NULLLoggerConfig(EventHandlerConfig):
    def __init__(self, name: str = DEFAULT_NULL_LOGGER_NAME):
        null_handler: EventWriterToNullHandler = EventWriterToNullHandler(name=name)
        handlers = [null_handler]
        super().__init__(handlers, handlers)
