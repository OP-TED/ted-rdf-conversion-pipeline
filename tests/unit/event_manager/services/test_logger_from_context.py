import pytest

from ted_sws.event_manager.adapters.event_handler_config import DAGLoggerConfig
from ted_sws.event_manager.adapters.event_log_decorator import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageProcessType, EventMessageMetadata
from ted_sws.event_manager.services.logger_from_context import get_logger_from_dag_context, \
    handle_event_message_metadata_context, handle_event_message_metadata_dag_context, \
    get_task_id_from_dag_context, get_dag_id_from_dag_context, get_dag_run_id_from_dag_context


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


def test_get_task_id_from_dag_context(fake_dag_context):
    assert get_task_id_from_dag_context(fake_dag_context)


def test_get_dag_id_from_dag_context(fake_dag_context):
    assert get_dag_id_from_dag_context(fake_dag_context)


def test_get_dag_run_id_from_dag_context(fake_dag_context):
    assert get_dag_run_id_from_dag_context(fake_dag_context)


def test_handle_event_message_metadata_dag_context(fake_dag_context):
    process_name = "DAG_NAME"
    process_id = "DAG_RUN_ID"

    metadata = handle_event_message_metadata_dag_context(ps_name=process_name, ps_id=process_id, ps_context={})
    assert metadata.process_id == process_id
    assert metadata.process_name == process_name

    metadata = handle_event_message_metadata_dag_context(dag_context=fake_dag_context)
    assert metadata.process_id
    assert metadata.process_name
    assert metadata.process_context['task_id']


def test_handle_event_message_metadata_context():
    process_name = "DAG_NAME"
    process_id = "DAG_RUN_ID"
    process_type = EventMessageProcessType.CLI

    event_message: EventMessage = EventMessage(metadata=EventMessageMetadata())
    metadata = handle_event_message_metadata_context(event_message=event_message, ps_type=process_type,
                                                     ps_name=process_name, ps_id=process_id,
                                                     ps_context={"context_var": True})
    assert metadata.process_type == process_type
    assert metadata.process_id == process_id
    assert metadata.process_name == process_name
    assert metadata.process_context
    assert metadata.process_context['context_var']

