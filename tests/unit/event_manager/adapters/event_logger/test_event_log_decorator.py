import os
from unittest import mock

import pytest
from airflow.utils.context import Context

from ted_sws import RUN_ENV_NAME, RUN_ENV_VAL
from ted_sws.event_manager.adapters.event_handler_config import DAGLoggerConfig, NULLLoggerConfig
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.event_manager.services.logger_from_context import get_logger_from_dag_context, get_dag_args_from_context

deco_event_message = EventMessage(**{"title": "DAG_TEST_EVENT_MESSAGE_TITLE",
                                     "message": "DAG_TEST_EVENT_MESSAGE_MESSAGE"})


@event_log(event_message=deco_event_message,
           event_handler_config=DAGLoggerConfig(
               name="TEST_DAG_CONTEXT_LOGGER",
               config_handlers=ConfigHandlerType.ConsoleHandler.value
           ))
def assert_dag_event_log_decorator(caplog, event_message, **kwargs):
    with pytest.raises(ValueError):
        get_logger_from_dag_context({})
    logger = get_logger_from_dag_context(kwargs)
    logger.event_handler_config.get_console_handler().logger.propagate = True
    assert isinstance(logger, EventLogger)
    dag_run_id = "DAG_RUN_ID"
    dag_context: Context = Context(**{"run_id": dag_run_id})
    event_message.kwargs = get_dag_args_from_context(dag_context)
    assert event_message.kwargs['DAG']['RUN_ID'] == dag_run_id
    logger.info(event_message=event_message)
    assert event_message.message in caplog.text
    assert dag_run_id in caplog.text


@event_log()
def assert_event_log_decorator_within_test_env(**kwargs):
    logger = get_logger_from_dag_context(kwargs)
    assert isinstance(logger.event_handler_config, NULLLoggerConfig)


@mock.patch.dict(os.environ, {RUN_ENV_NAME: RUN_ENV_VAL})
def test_dag_event_log_decorator(caplog, event_message):
    assert_dag_event_log_decorator(caplog, event_message)
    assert deco_event_message.message in caplog.text


def test_event_log_decorator_within_test_env():
    assert_event_log_decorator_within_test_env()
