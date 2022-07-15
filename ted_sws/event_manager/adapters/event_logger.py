from ted_sws.event_manager.adapters.event_handler import EventHandler
from ted_sws.event_manager.adapters.event_handler_config import EventHandlerConfig
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageLogSettings
from ted_sws.event_manager.adapters.log import SeverityLevelType
from typing import Type, List, Union

HandlerType = Union[Type[EventHandler], List[Type[EventHandler]]]


"""
This module contains the event logger adapter.
"""


class EventLogger:
    """
    This is the event logger class.
    """
    event_handler_config: EventHandlerConfig

    def __init__(self, event_handler_config: EventHandlerConfig):
        """
        This is the constructor/initialization of event logger.

        :param event_handler_config: The event handler config for this event logger instance
        """
        self.event_handler_config = event_handler_config

    def debug(self, event_message: EventMessage, handler_type: HandlerType = None,
              settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        Logs an event message with level DEBUG on this event logger.

        :param event_message: The event message
        :param handler_type: The specific handler(s)
        :param settings: The logging settings
        :return: None
        """
        self.log(SeverityLevelType.DEBUG, event_message, handler_type, settings)

    def info(self, event_message: EventMessage, handler_type: HandlerType = None,
             settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        Logs an event message with level INFO on this event logger.

        :param event_message: The event message
        :param handler_type: The specific handler(s)
        :param settings: The logging settings
        :return: None
        """
        self.log(SeverityLevelType.INFO, event_message, handler_type, settings)

    def warning(self, event_message: EventMessage, handler_type: HandlerType = None,
                settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        Logs an event message with level WARNING on this event logger.

        :param event_message: The event message
        :param handler_type: The specific handler(s)
        :param settings: The logging settings
        :return: None
        """
        self.log(SeverityLevelType.WARNING, event_message, handler_type, settings)

    def error(self, event_message: EventMessage, handler_type: HandlerType = None,
              settings: EventMessageLogSettings = EventMessageLogSettings()):
        """
        Logs an event message with level ERROR on this event logger.

        :param event_message: The event message
        :param handler_type: The specific handler(s)
        :param settings: The logging settings
        :return: None
        """
        self.log(SeverityLevelType.ERROR, event_message, handler_type, settings)

    @classmethod
    def _apply_handler(cls, handler_type: HandlerType, event_handler: EventHandler) -> bool:
        """
        To use or not the specific handler(s)

        :param handler_type: Specific handler(s) to be used
        :param event_handler: Event logger handler
        :return: True or False
        """
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
        """
        Logs an event message with severity level on this event logger.

        :param severity_level: The logging severity level
        :param event_message: The event message to be logged
        :param handler_type: Specific event handler(s) to be used, otherwise the default ones will be used
        :param settings: The logging settings
        :return: None
        """
        if handler_type and settings.force_handlers:
            handlers = self.event_handler_config.get_prime_handlers()
        else:
            handlers = self.event_handler_config.get_handlers()

        for event_handler in handlers:
            if self._apply_handler(handler_type, event_handler):
                event_handler.log(severity_level, event_message, settings)
