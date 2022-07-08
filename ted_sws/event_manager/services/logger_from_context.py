from airflow.utils.context import Context

from ted_sws.event_manager.adapters.event_handler_config import CLILoggerConfig, NULLLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.adapters.log import EVENT_LOGGER_CONTEXT_KEY
from ted_sws.event_manager.adapters.log import is_env_logging_enabled
from ted_sws.event_manager.model.event_message import EventMessage


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


def get_dag_args_from_context(context: Context, args: dict = None) -> dict:
    if not args:
        args = {}
    if 'DAG' not in args:
        args['DAG'] = {}
    args['DAG']['RUN_ID'] = context['run_id']

    return args
