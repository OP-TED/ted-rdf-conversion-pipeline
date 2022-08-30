from typing import Dict, Any, MutableMapping, Union

from ted_sws.event_manager.adapters.event_handler_config import NULLLoggerConfig, ConsoleLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.adapters.log import is_env_logging_enabled
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageProcessType, EventMessageMetadata

ContextType = Union[Dict[str, Any], MutableMapping[str, Any]]

"""
This module contains event logger tools.
"""


def get_env_logger(logger: EventLogger, is_cli: bool = False) -> EventLogger:
    """
    This method returns the event logger, based on environment:
     - if not test environment: logger
     - if test environment and called from CLI command (is_cli): logger with only console handler configured
     - if test environment (not cli): logger with only null handler configured

    :param logger: The default logger
    :param is_cli: Is called from a CLI command?
    :return: The environment based event logger
    """
    if is_env_logging_enabled():
        return logger
    elif is_cli:
        logger_config = ConsoleLoggerConfig()
        logger_config.get_console_handler().logger.propagate = True
        return EventLogger(logger_config)
    else:
        return EventLogger(NULLLoggerConfig())


def get_logger_from_dag_context(dag_context: dict) -> EventLogger:
    """
    Get event logger injected into "host" function by event_log decorator.

    :param dag_context: The args that event logger was injected in
    :return: The injected event logger
    """
    if EVENT_LOGGER_CONTEXT_KEY in dag_context:
        return dag_context[EVENT_LOGGER_CONTEXT_KEY]
    else:
        raise ValueError("No event_logger available!")


def get_task_id_from_dag_context(dag_context: ContextType) -> str:
    return dag_context['task'].task_id


def get_dag_run_id_from_dag_context(dag_context: ContextType) -> str:
    return dag_context['dag_run'].run_id


def get_dag_id_from_dag_context(dag_context: ContextType) -> str:
    return dag_context['dag'].dag_id


def handle_event_message_metadata_dag_context(event_message: EventMessage = None, dag_context: ContextType = None,
                                              ps_name: str = None, ps_id: str = None,
                                              ps_context: Dict[str, Any] = None) -> EventMessageMetadata:
    """
    Update event message metadata with data from DAG context.

    :param event_message: The event message
    :param dag_context: The DAG context
    :param ps_name: The process name
    :param ps_id: The process id
    :param ps_context: The process context
    :return: The event message metadata
    """
    metadata = handle_event_message_metadata_context(event_message, EventMessageProcessType.DAG,
                                                     ps_name, ps_id, ps_context)

    if dag_context:
        if not metadata.process_id:
            metadata.process_id = get_dag_run_id_from_dag_context(dag_context)

        if not metadata.process_context:
            metadata.process_context = {}

        metadata.process_context["task_id"] = get_task_id_from_dag_context(dag_context)
        metadata.process_context["params"] = dag_context['params']

        if not metadata.process_name:
            metadata.process_name = get_dag_id_from_dag_context(dag_context)

    return metadata


def handle_event_message_metadata_context(event_message: EventMessage = None, ps_type: EventMessageProcessType = None,
                                          ps_name: str = None, ps_id: str = None,
                                          ps_context: Dict[str, Any] = None) -> EventMessageMetadata:
    """
    Update event message metadata with data from process context.

    :param event_message: The event message
    :param ps_type: The process type
    :param ps_name: The process name
    :param ps_id: The process id
    :param ps_context: The process context
    :return: The event message metadata
    """
    metadata: EventMessageMetadata = EventMessageMetadata()
    if event_message is not None and event_message.metadata:
        metadata = event_message.metadata

    if ps_type:
        metadata.process_type = ps_type

    if ps_name:
        metadata.process_name = ps_name

    if ps_id:
        metadata.process_id = ps_id

    if ps_context:
        metadata.process_context = ps_context

    if event_message is not None:
        event_message.metadata = metadata

    return metadata
