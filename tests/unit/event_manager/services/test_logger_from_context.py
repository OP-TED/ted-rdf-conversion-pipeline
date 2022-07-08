import pytest
from airflow.utils.context import Context

from ted_sws.event_manager.adapters.event_handler_config import DAGLoggerConfig
from ted_sws.event_manager.adapters.event_log_decorator import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.services.logger_from_context import get_logger_from_dag_context, get_dag_args_from_context


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


def test_get_dag_args_from_context():
    dag_name = "DAG_NAME"
    dag_run_id = "DAG_RUN_ID"
    dag_context: Context = Context(**{"run_id": dag_run_id})
    kwargs = get_dag_args_from_context(dag_context, name=dag_name)
    assert kwargs['DAG']['RUN_ID'] == dag_run_id
    assert kwargs['DAG']['NAME'] == dag_name

    args: dict = {'DAG': {'RUNNABLE': True}}
    kwargs = get_dag_args_from_context(dag_context, args=args)
    assert kwargs['DAG']['RUN_ID'] == dag_run_id
    assert kwargs['DAG']['RUNNABLE']


