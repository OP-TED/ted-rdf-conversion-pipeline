import logging
from typing import List

from ted_sws.event_manager.adapters.log.common import LoggingHandler, DOMAIN_LOGGING_HANDLERS, DEFAULT_LOGGER_LEVEL, \
    DEFAULT_LOGGER_NAME, LOGGING_HANDLERS_TYPE
from ted_sws.event_manager.adapters.log.logger_abc import LoggerABC
from ted_sws.event_manager.adapters.log.logger_mongo_handler import BufferedMongoHandler as LoggerMongoHandler
from ted_sws.event_manager.adapters.log.logger_stream_handler import StreamHandler as LoggerStreamHandler


class Logger(LoggerABC):
    """
    This class provides common features for available loggers
    """

    def __init__(self, name: str = DEFAULT_LOGGER_NAME, level: int = DEFAULT_LOGGER_LEVEL,
                 logging_handlers: LOGGING_HANDLERS_TYPE = None):
        if logging_handlers is None:
            logging_handlers = DOMAIN_LOGGING_HANDLERS
        self.level = level
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logging_handlers = logging_handlers
        # self.logger.propagate = False

        self.add_handlers()

    def get_logger(self) -> logging.Logger:
        return self.logger

    def has_logging_handler(self, logging_handler: LoggingHandler):
        return logging_handler.value in self.logging_handlers

    def init_handlers(self):
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

    def get_handlers(self) -> List:
        return self.logger.handlers

    def add_handlers(self):
        self.init_handlers()
        if self.has_logging_handler(LoggingHandler.STREAM):
            self.add_stream_handler()
        if self.has_logging_handler(LoggingHandler.MONGO):
            self.add_mongo_handler()

    def has_handler(self, handler) -> bool:
        return any((type(handler) is type(h)) for h in self.get_handlers())

    def add_handler(self, handler):
        if not self.has_handler(handler):
            self.logger.addHandler(handler)

    def log(self, record, level: int = None, **kwargs):
        self.logger.log(level if level is not None else self.level, record, **kwargs)

    def add_mongo_handler(self, level: int = DEFAULT_LOGGER_LEVEL, formatter: logging.Formatter = None):
        handler = LoggerMongoHandler(
            level=level,
            formatter=formatter
        )

        self.add_handler(handler)

    def add_stream_handler(self, level: int = DEFAULT_LOGGER_LEVEL, formatter: logging.Formatter = None):
        handler: LoggerStreamHandler = LoggerStreamHandler(level, formatter)
        self.add_handler(handler)
