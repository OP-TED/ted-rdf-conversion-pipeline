from ted_sws.event_manager.adapters.event_handler_config import EventHandlerConfig
from ted_sws.event_manager.model.event_message import EventMessage, SeverityLevelType


class EventLogger:
    event_handler_config: EventHandlerConfig

    def __init__(self, event_handler_config: EventHandlerConfig):
        self.event_handler_config = event_handler_config

    def debug(self, event_message: EventMessage):
        self.log(SeverityLevelType.DEBUG, event_message)

    def info(self, event_message: EventMessage):
        self.log(SeverityLevelType.INFO, event_message)

    def warning(self, event_message: EventMessage):
        self.log(SeverityLevelType.WARNING, event_message)

    def error(self, event_message: EventMessage):
        self.log(SeverityLevelType.ERROR, event_message)

    def log(self, severity_level: SeverityLevelType, event_message: EventMessage):
        for event_handler in self.event_handler_config.get_handlers():
            event_handler.log(severity_level, event_message)
