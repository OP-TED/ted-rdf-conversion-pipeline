import pytest

from ted_sws.event_manager.adapters.event_handler_config import DAGLoggerConfig
from ted_sws.event_manager.adapters.event_log_decorator import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageProcessType, EventMessageMetadata
from ted_sws.event_manager.services.logger_from_context import get_logger_from_dag_context, \
    handle_event_message_metadata_context, handle_event_message_metadata_dag_context


def test_get_logger_from_dag_context():
    with pytest.raises(ValueError):
        get_logger_from_dag_context({})
    kwargs: dict = {
        EVENT_LOGGER_CONTEXT_KEY: EventLogger(event_handler_config=DAGLoggerConfig(
            name="TEST_DAG_CONTEXT_LOGGER",
            config_handlers=ConfigHandlerType.ConsoleHandler.value
        ))
    }
    logger = get_logger_from_dag_context(kwargs)
    assert isinstance(logger, EventLogger)


def test_handle_event_message_metadata_dag_context():
    process_name = "DAG_NAME"
    process_id = "DAG_RUN_ID"

    context = {"run_id": process_id}
    metadata = handle_event_message_metadata_dag_context(ps_name=process_name, context=context)
    assert metadata.process_id == process_id
    assert metadata.process_name == process_name


def test_handle_event_message_metadata_context():
    process_name = "DAG_NAME"
    process_id = "DAG_RUN_ID"
    process_type = EventMessageProcessType.DAG

    context = {"run_id": process_id}
    metadata = handle_event_message_metadata_context(ps_type=process_type, ps_name=process_name, context=context)
    assert metadata.process_id == process_id
    assert metadata.process_name == process_name

    event_message = EventMessage()
    event_message.metadata = EventMessageMetadata(**{'process_name': process_name})
    handle_event_message_metadata_context(event_message, ps_type=process_type, context=context)
    assert event_message.metadata.process_name == process_name
    assert event_message.metadata.process_type == process_type
