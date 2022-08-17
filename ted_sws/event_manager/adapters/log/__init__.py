import logging
import os
from enum import Enum

from ted_sws import RUN_ENV_NAME, RUN_TEST_ENV_VAL

from colorama import Fore

LOG_ERROR_TEXT = Fore.RED + "{}" + Fore.RESET
LOG_SUCCESS_TEXT = Fore.GREEN + "{}" + Fore.RESET
LOG_INFO_TEXT = Fore.CYAN + "{}" + Fore.RESET
LOG_WARN_TEXT = Fore.YELLOW + "{}" + Fore.RESET


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


def is_env_logging_enabled() -> bool:
    return os.environ[RUN_ENV_NAME] not in [RUN_TEST_ENV_VAL]
