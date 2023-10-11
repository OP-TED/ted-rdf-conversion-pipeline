from ted_sws.event_manager.adapters.event_logger import EventMessageLogSettings
from ted_sws.event_manager.model.event_message import EventMessage, TechnicalEventMessage, NoticeEventMessage, \
    MappingSuiteEventMessage
from ted_sws.event_manager.services.logger_from_context import get_logger, get_cli_logger


def log_info(message: str, name: str = None):
    """
    Logs INFO EventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).info(event_message=EventMessage(message=message))


def log_error(message: str, name: str = None):
    """
    Logs ERROR EventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).error(event_message=EventMessage(message=message))


def log_debug(message: str, name: str = None):
    """
    Logs DEBUG EventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).debug(event_message=EventMessage(message=message))


def log_warning(message: str, name: str = None):
    """
    Logs WARNING EventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).warning(event_message=EventMessage(message=message))


def log_technical_info(message: str, name: str = None):
    """
    Logs INFO TechnicalEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).info(event_message=TechnicalEventMessage(message=message))


def log_technical_error(message: str, name: str = None):
    """
    Logs ERROR TechnicalEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).error(event_message=TechnicalEventMessage(message=message))


def log_technical_debug(message: str, name: str = None):
    """
    Logs DEBUG TechnicalEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).debug(event_message=TechnicalEventMessage(message=message))


def log_technical_warning(message: str, name: str = None):
    """
    Logs WARNING TechnicalEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).warning(event_message=TechnicalEventMessage(message=message))


def log_notice_info(message: str, notice_id: str = None, name: str = None):
    """
    Logs INFO NoticeEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param notice_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).info(event_message=NoticeEventMessage(message=message, notice_id=notice_id))


def log_notice_error(message: str, notice_id: str = None, name: str = None, domain_action: str = None,
                     notice_form_number: str = None, notice_eforms_subtype: str = None, notice_status: str = None):
    """
    Logs ERROR NoticeEventMessage, using global (DAG) logger or a custom named one
    :param domain_action:
    :param notice_form_number:
    :param notice_eforms_subtype:
    :param notice_status:
    :param message:
    :param notice_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).error(
        event_message=NoticeEventMessage(message=message, notice_id=notice_id, domain_action=domain_action,
                                         notice_form_number=notice_form_number,
                                         notice_eforms_subtype=notice_eforms_subtype, notice_status=notice_status))


def log_notice_debug(message: str, notice_id: str = None, name: str = None):
    """
    Logs DEBUG NoticeEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param notice_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).debug(event_message=NoticeEventMessage(message=message, notice_id=notice_id))


def log_notice_warning(message: str, notice_id: str = None, name: str = None):
    """
    Logs WARNING NoticeEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param notice_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).warning(event_message=NoticeEventMessage(message=message, notice_id=notice_id))


def log_mapping_suite_info(message: str, mapping_suite_id: str = None, name: str = None):
    """
    Logs INFO MappingSuiteEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param mapping_suite_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).info(
        event_message=MappingSuiteEventMessage(message=message, mapping_suite_id=mapping_suite_id))


def log_mapping_suite_error(message: str, mapping_suite_id: str = None, name: str = None):
    """
    Logs ERROR MappingSuiteEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param mapping_suite_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).error(
        event_message=MappingSuiteEventMessage(message=message, mapping_suite_id=mapping_suite_id))


def log_mapping_suite_debug(message: str, mapping_suite_id: str = None, name: str = None):
    """
    Logs DEBUG MappingSuiteEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param mapping_suite_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).debug(
        event_message=MappingSuiteEventMessage(message=message, mapping_suite_id=mapping_suite_id))


def log_mapping_suite_warning(message: str, mapping_suite_id: str = None, name: str = None):
    """
    Logs WARNING MappingSuiteEventMessage, using global (DAG) logger or a custom named one
    :param message:
    :param mapping_suite_id:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_logger(name=name).warning(
        event_message=MappingSuiteEventMessage(message=message, mapping_suite_id=mapping_suite_id))


def log_cli_brief_notice_info(message: str, name: str = None):
    """
    Logs brief (just the message) INFO NoticeEventMessage, using global (CLI) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_cli_logger(name=name).info(
        event_message=NoticeEventMessage(message=message),
        settings=EventMessageLogSettings(briefly=True)
    )


def log_cli_brief_notice_error(message: str, name: str = None):
    """
    Logs brief (just the message) ERROR NoticeEventMessage, using global (CLI) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_cli_logger(name=name).error(
        event_message=NoticeEventMessage(message=message),
        settings=EventMessageLogSettings(briefly=True)
    )


def log_cli_brief_info(message: str, name: str = None):
    """
    Logs brief (just the message) INFO EventMessage, using global (CLI) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_cli_logger(name=name).info(
        event_message=EventMessage(message=message),
        settings=EventMessageLogSettings(briefly=True)
    )


def log_cli_brief_error(message: str, name: str = None):
    """
    Logs brief (just the message) ERROR EventMessage, using global (CLI) logger or a custom named one
    :param message:
    :param name: Logger name (None to use the global logger)
    :return:
    """
    get_cli_logger(name=name).error(
        event_message=EventMessage(message=message),
        settings=EventMessageLogSettings(briefly=True)
    )
