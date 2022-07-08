from decorator import decorate

from ted_sws.event_manager.adapters.event_handler import DEFAULT_SEVERITY_LEVEL
from ted_sws.event_manager.adapters.event_handler_config import EventHandlerConfig, DAGLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.model.event_message import EventMessage, SeverityLevelType
from ted_sws.event_manager.services.logger_from_context import get_env_logger

DEFAULT_DAG_LOGGER_NAME = "DAG"


# Event Log decorator


def event_log(
        event_message: EventMessage = EventMessage(),
        event_handler_config: EventHandlerConfig = DAGLoggerConfig(
            name=DEFAULT_DAG_LOGGER_NAME
        ),
        severity_level: SeverityLevelType = DEFAULT_SEVERITY_LEVEL,
        is_loggable: bool = True,
        inject_logger: bool = True
):
    def wrapper(fn):
        def log(event_logger: EventLogger) -> EventMessage:
            if not event_message.caller_name:
                event_message.caller_name = fn.__name__
            event_logger.log(severity_level, event_message)
            return event_message

        def process(fn, *args, **kwargs):
            is_event_message_loggable: bool = is_loggable and event_message
            init_logger: bool = inject_logger or is_loggable
            if init_logger:
                event_logger = get_env_logger(EventLogger(event_handler_config))

            if inject_logger:
                kwargs[EVENT_LOGGER_CONTEXT_KEY] = event_logger

            if is_event_message_loggable:
                event_message.start()

            result = fn(*args, **kwargs)

            if is_event_message_loggable:
                event_message.end()
                log(event_logger)

            return result

        return decorate(fn, process)

    return wrapper
