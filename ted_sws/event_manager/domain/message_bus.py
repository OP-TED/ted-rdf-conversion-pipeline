import logging
from typing import Callable, List, Dict

from pymessagebus import MessageBus as PyMessageBus
from pymessagebus.api import Middleware
from pymessagebus.middleware.logger import get_logger_middleware, LoggingMiddlewareConfig

from ted_sws.event_manager.adapters.log.logger import Logger
from ted_sws.event_manager.domain import message_handlers
from ted_sws.event_manager.model import message

""" 
Here is instantiated/initialized domain message_bus service
"""


class MessageBus(PyMessageBus):
    """
    This class provides additional features to MessageBus
    """
    _logger: Logger = None

    def set_middlewares(self, _middlewares: List[Middleware] = None):
        self._middlewares_chain = self._get_middlewares_callables_chain(
            _middlewares, self._trigger_handlers_for_message_as_a_middleware
        )

    def add_handlers(self, handlers: Dict[type, List[Callable]]) -> None:
        for message_class in handlers:
            for message_handler in handlers[message_class]:
                super().add_handler(message_class, message_handler)


message_bus = MessageBus()

message_bus.add_handlers({
    message.Log: [
        message_handlers.handler_log
    ]
})
