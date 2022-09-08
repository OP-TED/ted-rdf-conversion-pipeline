from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.event_manager.services.logger_from_context import get_logger


def log_info(message: str, name: str = None):
    get_logger(name=name).info(event_message=EventMessage(message=message))


def log_error(message: str, name: str = None):
    get_logger(name=name).error(event_message=EventMessage(message=message))


def log_debug(message: str, name: str = None):
    get_logger(name=name).debug(event_message=EventMessage(message=message))
