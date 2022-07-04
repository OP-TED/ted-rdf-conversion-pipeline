from datetime import datetime, timezone

from decorator import decorate

from ted_sws.event_manager.adapters.event_handler_config import EventHandlerConfig, DAGLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import is_event_loggable
from ted_sws.event_manager.model.event_message import EventMessage, SeverityLevelType


# Event Log decorator


def log(event_message_type: EventMessage, title: str = '', message: str = '',
        event_handler_config: EventHandlerConfig = DAGLoggerConfig,
        severity_level: SeverityLevelType = SeverityLevelType.INFO, **extra_args):
    def wrapper(fn):
        def log_save_before(event_logger: EventLogger):
            event_message = event_message_type.__init__()
            event_message.title = title
            event_message.message = message
            event_message.caller_name = fn.__name__
            event_message.args = {**extra_args}
            event_logger.log(severity_level, event_message)
            return event_message

        def log_save_after(event_logger: EventLogger, event_message: EventMessage, started_at, ended_at):
            event_message.duration = (ended_at - started_at).total_seconds()
            event_logger.log(severity_level, event_message)

        def process(fn, *args, **kwargs):
            if not is_event_loggable():
                return fn(*args, **kwargs)

            event_logger = EventLogger(event_handler_config=event_handler_config)

            started_at = datetime.now(timezone.utc)
            event_message = log_save_before(event_logger)
            result = fn(event_logger=event_logger, *args, **kwargs)
            ended_at = datetime.now(timezone.utc)
            log_save_after(event_logger, event_message, started_at, ended_at)

            return result

        return decorate(fn, process)

    return wrapper
