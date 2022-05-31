import enum
import logging
from typing import List

from colorama import Fore

from ted_sws import config


class LoggingHandler(enum.Enum):
    STREAM = "STREAM"
    MONGO = "MONGO"


LOGGING_HANDLERS_TYPE = List[str]
DOMAIN_LOGGING_HANDLERS: LOGGING_HANDLERS_TYPE = config.LOGGER_LOGGING_HANDLER.split(
    ",") if config.LOGGER_LOGGING_HANDLER is not None else [LoggingHandler.STREAM.value]
DEFAULT_LOGGER_LEVEL = logging.NOTSET
DEFAULT_LOGGER_NAME = "ROOT"

LOG_ERROR_TEXT = Fore.RED + "{}" + Fore.RESET
LOG_SUCCESS_TEXT = Fore.GREEN + "{}" + Fore.RESET
LOG_INFO_TEXT = Fore.CYAN + "{}" + Fore.RESET
LOG_WARN_TEXT = Fore.YELLOW + "{}" + Fore.RESET

LOG_ERROR_LEVEL = logging.ERROR
LOG_INFO_LEVEL = logging.INFO
LOG_WARN_LEVEL = logging.WARNING
