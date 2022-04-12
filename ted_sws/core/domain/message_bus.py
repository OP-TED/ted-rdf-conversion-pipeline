import logging
from typing import Callable, List, Dict

from pymessagebus import MessageBus as PyMessageBus
from pymessagebus.api import Middleware
from pymessagebus.middleware.logger import get_logger_middleware, LoggingMiddlewareConfig

from ted_sws.core.adapters.logger import logger, Logger
from ted_sws.core.domain import message_handlers
from ted_sws.core.model import message

""" 
Here is instantiated/initialized domain message_bus service
"""


class MessageBus(PyMessageBus):
    """
    This class provides additional features to MessageBus
    """
    HAS_LOGGING_MIDDLEWARE = True
    _logger: Logger = logger

    def set_domain_logger(self, _logger: Logger):
        self._logger = _logger

    def get_domain_logger(self) -> Logger:
        return self._logger

    def set_middlewares(self, _middlewares: List[Middleware] = None):
        self._middlewares_chain = self._get_middlewares_callables_chain(
            _middlewares, self._trigger_handlers_for_message_as_a_middleware
        )

    def add_handlers(self, handlers: Dict[type, List[Callable]]) -> None:
        for message_class in handlers:
            for message_handler in handlers[message_class]:
                super().add_handler(message_class, message_handler)


message_bus = MessageBus()

middlewares: List = []
if MessageBus.HAS_LOGGING_MIDDLEWARE:
    logging_middleware_config = LoggingMiddlewareConfig(
        mgs_received_level=logging.INFO,
        mgs_succeeded_level=logging.INFO,
        mgs_failed_level=logging.CRITICAL
    )
    logging_middleware = get_logger_middleware(message_bus.get_domain_logger().get_logger(), logging_middleware_config)
    middlewares.append(logging_middleware)

if len(middlewares) > 0:
    message_bus.set_middlewares(middlewares)

message_bus.add_handlers({message.Log: [message_handlers.handler_log]})
