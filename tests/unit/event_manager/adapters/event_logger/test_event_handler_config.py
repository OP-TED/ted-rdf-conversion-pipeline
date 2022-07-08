from ted_sws.event_manager.adapters.event_handler_config import DAGLoggerConfig, CLILoggerConfig, NULLLoggerConfig
from ted_sws.event_manager.adapters.event_handler import EventWriterToConsoleHandler, EventWriterToNullHandler


def test_event_handler_config(mongodb_client, event_logs_filepath, prime_config_handlers):
    logger_config = DAGLoggerConfig(mongodb_client=mongodb_client, filepath=event_logs_filepath,
                                    config_handlers=prime_config_handlers)
    assert logger_config.init_logger_name()
    assert logger_config.init_log_filepath()
    assert len(logger_config.get_handlers()) == 3

    console_handler = logger_config.get_console_handler()
    assert console_handler and isinstance(console_handler, EventWriterToConsoleHandler)

    logger_config = CLILoggerConfig(mongodb_client=mongodb_client, filepath=event_logs_filepath,
                                    config_handlers='')
    assert len(logger_config.get_prime_handlers()) == 3


def test_event_null_handler_config():
    logger_config = NULLLoggerConfig()
    assert len(logger_config.get_handlers()) == 1
    assert isinstance(logger_config.get_handler(EventWriterToNullHandler), EventWriterToNullHandler)
