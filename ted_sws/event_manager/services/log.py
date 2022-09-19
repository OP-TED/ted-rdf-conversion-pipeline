from ted_sws.event_manager.model.event_message import EventMessage, TechnicalEventMessage, NoticeEventMessage, \
    MappingSuiteEventMessage
from ted_sws.event_manager.adapters.event_logger import EventMessageLogSettings
from ted_sws.event_manager.services.logger_from_context import get_logger, get_cli_logger


def log_info(message: str, name: str = None):
    get_logger(name=name).info(event_message=EventMessage(message=message))


def log_error(message: str, name: str = None):
    get_logger(name=name).error(event_message=EventMessage(message=message))


def log_debug(message: str, name: str = None):
    get_logger(name=name).debug(event_message=EventMessage(message=message))


def log_warning(message: str, name: str = None):
    get_logger(name=name).warning(event_message=EventMessage(message=message))


def log_technical_info(message: str, name: str = None):
    get_logger(name=name).info(event_message=TechnicalEventMessage(message=message))


def log_technical_error(message: str, name: str = None):
    get_logger(name=name).error(event_message=TechnicalEventMessage(message=message))


def log_technical_debug(message: str, name: str = None):
    get_logger(name=name).debug(event_message=TechnicalEventMessage(message=message))


def log_technical_warning(message: str, name: str = None):
    get_logger(name=name).warning(event_message=TechnicalEventMessage(message=message))


def log_notice_info(message: str, name: str = None):
    get_logger(name=name).info(event_message=NoticeEventMessage(message=message))


def log_notice_error(message: str, name: str = None):
    get_logger(name=name).error(event_message=NoticeEventMessage(message=message))


def log_notice_debug(message: str, name: str = None):
    get_logger(name=name).debug(event_message=NoticeEventMessage(message=message))


def log_notice_warning(message: str, name: str = None):
    get_logger(name=name).warning(event_message=NoticeEventMessage(message=message))


def log_mapping_suite_info(message: str, name: str = None):
    get_logger(name=name).info(event_message=MappingSuiteEventMessage(message=message))


def log_mapping_suite_error(message: str, name: str = None):
    get_logger(name=name).error(event_message=MappingSuiteEventMessage(message=message))


def log_mapping_suite_debug(message: str, name: str = None):
    get_logger(name=name).debug(event_message=MappingSuiteEventMessage(message=message))


def log_mapping_suite_warning(message: str, name: str = None):
    get_logger(name=name).warning(event_message=MappingSuiteEventMessage(message=message))


def log_cli_brief_notice_info(message: str, name: str = None):
    get_cli_logger(name=name).info(
        event_message=NoticeEventMessage(message=message),
        settings=EventMessageLogSettings(briefly=True)
    )
