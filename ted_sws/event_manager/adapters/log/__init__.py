from ted_sws import RUN_ENV_NAME, RUN_TEST_ENV_VAL
import os
from enum import Enum
import logging

EVENT_LOGGER_CONTEXT_KEY = '__event_logger__'


class SeverityLevelType(Enum):
    NOTSET = logging.NOTSET,
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class ConfigHandlerType(Enum):
    ConsoleHandler = "ConsoleHandler"
    FileHandler = "FileHandler"
    MongoDBHandler = "MongoDBHandler"


class LoggedBy(Enum):
    DECORATOR = "decorator"
    WRITER = "writer"


def is_env_logging_enabled() -> bool:
    return os.environ[RUN_ENV_NAME] not in [RUN_TEST_ENV_VAL]
