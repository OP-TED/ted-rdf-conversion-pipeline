from pathlib import Path

import pytest

from ted_sws.event_manager.adapters.event_handler import EventHandler, EventWriterToMongoDBHandler, \
    EventWriterToFileHandler, EventWriterToConsoleHandler, EventWriterToNullHandler
from ted_sws.event_manager.adapters.event_logging_repository import EventLoggingRepository, NoticeEventRepository, \
    TechnicalEventRepository, MappingSuiteEventRepository
from ted_sws.event_manager.adapters.log import ConfigHandlerType
from ted_sws.event_manager.adapters.log import SeverityLevelType
from ted_sws.event_manager.model.event_message import EventMessage, NoticeEventMessage, MappingSuiteEventMessage, \
    TechnicalEventMessage, EventMessageLogSettings


@pytest.fixture
def event_message() -> EventMessage:
    message = EventMessage()
    message.message = "TEST_EVENT_MESSAGE"
    return message


@pytest.fixture
def notice_event_message() -> NoticeEventMessage:
    message = NoticeEventMessage()
    message.message = "TEST_NOTICE_EVENT_MESSAGE"
    return message


@pytest.fixture
def mapping_suite_event_message() -> MappingSuiteEventMessage:
    message = MappingSuiteEventMessage()
    message.message = "TEST_MAPPING_SUITE_EVENT_MESSAGE"
    return message


@pytest.fixture
def technical_event_message() -> TechnicalEventMessage:
    message = TechnicalEventMessage()
    message.message = "TEST_TECHNICAL_EVENT_MESSAGE"
    return message


@pytest.fixture
def severity_level_debug() -> SeverityLevelType:
    return SeverityLevelType.DEBUG


@pytest.fixture
def severity_level_info() -> SeverityLevelType:
    return SeverityLevelType.INFO


@pytest.fixture
def severity_level_warning() -> SeverityLevelType:
    return SeverityLevelType.WARNING


@pytest.fixture
def severity_level_error() -> SeverityLevelType:
    return SeverityLevelType.ERROR


@pytest.fixture
def log_settings() -> EventMessageLogSettings:
    return EventMessageLogSettings()


@pytest.fixture
def event_handler() -> EventHandler:
    handler = EventHandler()
    return handler


@pytest.fixture
def console_handler() -> EventWriterToConsoleHandler:
    name = "TEST_CONSOLE_HANDLER"
    handler = EventWriterToConsoleHandler(name=name)
    handler.logger.propagate = True
    return handler


@pytest.fixture
def output_not_briefly_key() -> str:
    return 'caller_name'


@pytest.fixture
def event_logs_filepath() -> Path:
    return Path('./__test_event_messages__.log')


@pytest.fixture
def file_handler(event_logs_filepath) -> EventWriterToFileHandler:
    handler = EventWriterToFileHandler(filepath=event_logs_filepath)
    return handler


@pytest.fixture
def null_handler() -> EventWriterToNullHandler:
    name = "TEST_CONSOLE_HANDLER"
    handler = EventWriterToNullHandler(name=name)
    return handler


@pytest.fixture
def mongodb_handler(mongodb_client) -> EventWriterToMongoDBHandler:
    handler = EventWriterToMongoDBHandler(mongodb_client=mongodb_client)
    return handler


@pytest.fixture
def logs_database_name() -> str:
    return EventLoggingRepository.get_default_database_name()


@pytest.fixture
def event_logging_repository(mongodb_client, logs_database_name) -> EventLoggingRepository:
    repo = EventLoggingRepository(mongodb_client, logs_database_name)
    return repo


@pytest.fixture
def notice_event_repository(mongodb_client, logs_database_name) -> NoticeEventRepository:
    repo = NoticeEventRepository(mongodb_client, logs_database_name)
    return repo


@pytest.fixture
def technical_event_repository(mongodb_client, logs_database_name) -> TechnicalEventRepository:
    repo = TechnicalEventRepository(mongodb_client, logs_database_name)
    return repo


@pytest.fixture
def mapping_suite_event_repository(mongodb_client, logs_database_name) -> MappingSuiteEventRepository:
    repo = MappingSuiteEventRepository(mongodb_client, logs_database_name)
    return repo


@pytest.fixture
def prime_config_handlers() -> str:
    config_handlers = ConfigHandlerType.FileHandler.value + ',' + ConfigHandlerType.ConsoleHandler.value + ',' + ConfigHandlerType.MongoDBHandler.value
    return config_handlers
