from ted_sws.event_manager.adapters.event_handler import EventHandler
from ted_sws.event_manager.adapters.event_handler_config import EventHandlerConfig
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageLogSettings
from ted_sws.event_manager.adapters.log import SeverityLevelType
from typing import Type, List, Union

HandlerType = Union[Type[EventHandler], List[Type[EventHandler]]]


class EventLogger:
    event_handler_config: EventHandlerConfig

    def __init__(self, event_handler_config: EventHandlerConfig):
        self.event_handler_config = event_handler_config

    def debug(self, event_message: EventMessage, handler_type: HandlerType = None,
              settings: EventMessageLogSettings = EventMessageLogSettings()):
        self.log(SeverityLevelType.DEBUG, event_message, handler_type, settings)

    def info(self, event_message: EventMessage, handler_type: HandlerType = None,
             settings: EventMessageLogSettings = EventMessageLogSettings()):
        self.log(SeverityLevelType.INFO, event_message, handler_type, settings)

    def warning(self, event_message: EventMessage, handler_type: HandlerType = None,
                settings: EventMessageLogSettings = EventMessageLogSettings()):
        self.log(SeverityLevelType.WARNING, event_message, handler_type, settings)

    def error(self, event_message: EventMessage, handler_type: HandlerType = None,
              settings: EventMessageLogSettings = EventMessageLogSettings()):
        self.log(SeverityLevelType.ERROR, event_message, handler_type, settings)

    @classmethod
    def _apply_handler(cls, handler_type: HandlerType, event_handler: EventHandler) -> bool:
        if not handler_type:
            return True

        if not isinstance(handler_type, List):
            handler_type = [handler_type]

        for h in handler_type:
            if isinstance(event_handler, h):
                return True

        return False

    def log(
            self, severity_level: SeverityLevelType, event_message: EventMessage,
            handler_type: HandlerType = None,
            settings: EventMessageLogSettings = EventMessageLogSettings()
    ):
        if handler_type and settings.force_handlers:
            handlers = self.event_handler_config.get_prime_handlers()
        else:
            handlers = self.event_handler_config.get_handlers()

        for event_handler in handlers:
            if self._apply_handler(handler_type, event_handler):
                event_handler.log(severity_level, event_message, settings)
