import abc
from typing import List

from ted_sws import config
from ted_sws.event_manager.adapters.event_handler import EventHandler, EventWriterToStdoutHandler, \
    EventWriterToFileHandler, EventWriterToMongoDBHandler


class EventHandlerConfigABC(abc.ABC):
    @abc.abstractmethod
    def get_handlers(self) -> List[EventHandler]:
        pass


class EventHandlerConfig(EventHandlerConfigABC):
    config_handlers: List[str] = []
    handlers: List[EventHandler] = None

    def __init__(self):
        pass

    def get_handlers(self) -> List[EventHandler]:
        if self.handlers is None:
            self.handlers = []
            if "EventWriterToStdoutHandler" in self.config_handlers:
                self.handlers.append(EventWriterToStdoutHandler)
            if "EventWriterToFileHandler" in self.config_handlers:
                self.handlers.append(EventWriterToFileHandler)
            if "EventWriterToMongoDBHandler" in self.config_handlers:
                self.handlers.append(EventWriterToMongoDBHandler)

        return self.handlers


class DAGLoggerConfig(EventHandlerConfig):
    config_handlers: List[str] = config.DAG_LOGGER_CONFIG_HANDLERS.split(",")


class CLILoggerConfig(EventHandlerConfig):
    config_handlers: List[str] = config.CLI_LOGGER_CONFIG_HANDLERS.split(",")
