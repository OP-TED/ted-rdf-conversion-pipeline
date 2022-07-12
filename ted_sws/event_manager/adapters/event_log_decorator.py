from decorator import decorate

from ted_sws.event_manager.adapters.event_handler import DEFAULT_SEVERITY_LEVEL
from ted_sws.event_manager.adapters.event_handler_config import EventHandlerConfig, DAGLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.model.event_message import EventMessage, SeverityLevelType
from ted_sws.event_manager.services.logger_from_context import get_env_logger
import inspect

DEFAULT_DAG_LOGGER_NAME = "DAG"


"""
This module contains the event log decorator adapter.
"""


def event_log(
        event_message: EventMessage = EventMessage(),
        event_handler_config: EventHandlerConfig = DAGLoggerConfig(
            name=DEFAULT_DAG_LOGGER_NAME
        ),
        severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL,
        is_loggable: bool = True,
        inject_logger: bool = True
):
    """
    This is the event_log decorator to be used for method/process logging and event_logger injection.

    :param event_message: The base event message to be logged
    :param event_handler_config: The event handler config for event logger initialization
    :param severity_level: The logging severity level
    :param is_loggable: To log or not to log event message about "host" function
    :param inject_logger: To inject the event logger or not into "host" function
    :return: The decorator wrapper
    """
    def wrapper(fn):
        """
        The "host" function wrapper.

        :param fn: The "host" function
        :return: The process decorator
        """
        def log(event_logger: EventLogger) -> EventMessage:
            """
            Used to log the event message using event_logger instance.

            :param event_logger: Event logger instance
            :return: The logged event message
            """
            if not event_message.caller_name:
                event_message.caller_name = fn.__name__
            event_logger.log(severity_level, event_message)
            return event_message

        def fn_has_var_keyword_params() -> bool:
            """
            Used to check if "host" function has kwargs.

            :return: True or False
            """
            signature = inspect.signature(fn)
            params = signature.parameters.items()
            kwargs_param = next(filter(lambda p: (p[1].kind == inspect.Parameter.VAR_KEYWORD), params), None)
            return kwargs_param is not None

        def process(fn, *args, **kwargs):
            """
            This is the function that contains all the decorator's process logic.

            :param fn: The "host" function
            :param args: The positional function arguments
            :param kwargs: The keyword function arguments
            :return: The "host" function execution result
            """
            is_event_message_loggable: bool = is_loggable and event_message
            init_logger: bool = inject_logger or is_loggable
            if init_logger:
                event_logger = get_env_logger(EventLogger(event_handler_config))

            if inject_logger and fn_has_var_keyword_params():
                kwargs[EVENT_LOGGER_CONTEXT_KEY] = event_logger

            if is_event_message_loggable:
                event_message.start_record()

            result = fn(*args, **kwargs)

            if is_event_message_loggable:
                event_message.end_record()
                log(event_logger)

            return result

        return decorate(fn, process)

    return wrapper
