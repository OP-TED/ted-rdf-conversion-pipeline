from typing import Dict, Any, MutableMapping, Union

from ted_sws.event_manager.adapters.event_handler_config import CLILoggerConfig, NULLLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.adapters.log import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.adapters.log import is_env_logging_enabled
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageProcessType, EventMessageMetadata

ContextType = Union[Dict[str, Any], MutableMapping[str, Any]]


def get_env_logger(logger: EventLogger, is_cli: bool = False):
    if is_env_logging_enabled():
        return logger
    elif is_cli:
        logger_config = CLILoggerConfig(config_handlers=ConfigHandlerType.ConsoleHandler.value)
        logger_config.get_console_handler().logger.propagate = True
        return EventLogger(logger_config)
    else:
        return EventLogger(NULLLoggerConfig())


def get_logger_from_dag_context(dag_context: dict) -> EventLogger:
    if EVENT_LOGGER_CONTEXT_KEY in dag_context:
        return dag_context[EVENT_LOGGER_CONTEXT_KEY]
    else:
        raise ValueError("No event_logger available!")


def handle_event_message_metadata_dag_context(event_message: EventMessage = None, ps_name: str = None,
                                              context: ContextType = None) -> EventMessageMetadata:
    return handle_event_message_metadata_context(event_message, EventMessageProcessType.DAG, ps_name, context)


def handle_event_message_metadata_context(event_message: EventMessage = None, ps_type: EventMessageProcessType = None,
                                          ps_name: str = None, context: ContextType = None) -> EventMessageMetadata:
    metadata: EventMessageMetadata = EventMessageMetadata()
    if event_message is not None and event_message.metadata:
        metadata = event_message.metadata

    if ps_type:
        metadata.process_type = ps_type

    if ps_name:
        metadata.process_name = ps_name

    ps_id = None
    if ps_type == EventMessageProcessType.DAG:
        ps_id = context['run_id']

    if ps_id:
        metadata.process_id = ps_id

    if event_message is not None:
        event_message.metadata = metadata

    return metadata
