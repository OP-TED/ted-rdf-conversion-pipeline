import os

from ted_sws.event_manager.adapters.event_handler import EventWriterToFileHandler
from ted_sws.event_manager.adapters.event_handler_config import CLILoggerConfig, DEFAULT_CONSOLE_LOGGER_NAME
from ted_sws.event_manager.adapters.event_logger import EventLogger


def test_event_logger(console_handler, mongodb_handler, event_message, severity_level_info,
                      severity_level_debug, severity_level_error, severity_level_warning, event_logging_repository,
                      log_settings, event_logs_filepath):
    log: dict

    event_logger = EventLogger(CLILoggerConfig(handlers=[mongodb_handler], filepath=event_logs_filepath))
    collection = event_logging_repository.collection

    event_logger.log(severity_level_info, event_message)
    log = collection.find_one()
    assert log['message'] == event_message.message
    collection.delete_many({})

    event_logger.debug(event_message)
    log = collection.find_one()
    assert log['severity_level'] == severity_level_debug.value
    collection.delete_many({})

    event_logger.info(event_message)
    log = collection.find_one()
    assert log['severity_level'] == severity_level_info.value
    collection.delete_many({})

    event_logger.warning(event_message)
    log = collection.find_one()
    assert log['severity_level'] == severity_level_warning.value
    collection.delete_many({})

    event_logger.error(event_message)
    log = collection.find_one()
    assert log['severity_level'] == severity_level_error.value
    collection.delete_many({})

    log_settings.force_handlers = True
    event_logger.log(severity_level_info, event_message, EventWriterToFileHandler, log_settings)
    assert event_message.message in open(event_logs_filepath).read()

    os.remove(event_logs_filepath)


def test_event_logger_with_console_config(caplog, console_logger, event_message):
    console_logger.info(event_message)
    assert DEFAULT_CONSOLE_LOGGER_NAME in caplog.text
    assert event_message.message in caplog.text
