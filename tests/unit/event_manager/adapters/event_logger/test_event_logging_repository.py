import pytest
from bson import ObjectId

from ted_sws.event_manager.adapters.event_logging_repository import EventLoggingRepository


def assert_event_repository(event_repository, event_message, logs_database_name):
    assert EventLoggingRepository.get_default_database_name()

    _id = event_repository.add(event_message)
    assert _id
    log: dict = event_repository.collection.find_one({"_id": ObjectId(_id)})
    assert log['message'] == event_message.message

    event_repository.mongodb_client.drop_database(logs_database_name)


def test_event_logging_repository(logs_database_name, event_message, event_logging_repository):
    assert_event_repository(event_logging_repository, event_message, logs_database_name)

    db_name = "TEST_DB_NAME"
    collection_name = "TEST_COLLECTION_NAME"
    repository = EventLoggingRepository(event_logging_repository.mongodb_client, db_name, collection_name)
    assert repository.get_database_name() == db_name
    assert repository.get_collection_name() == collection_name

    event_message_dict: dict = repository.prepare_record(event_message)
    assert event_message_dict['message'] == event_message.message


def test_notice_event_repository(logs_database_name, notice_event_message, notice_event_repository):
    assert_event_repository(notice_event_repository, notice_event_message, logs_database_name)


def test_technical_event_repository(logs_database_name, technical_event_message, technical_event_repository):
    assert_event_repository(technical_event_repository, technical_event_message, logs_database_name)


def test_mapping_suite_event_repository(logs_database_name, mapping_suite_event_message,
                                        mapping_suite_event_repository):
    assert_event_repository(mapping_suite_event_repository, mapping_suite_event_message, logs_database_name)


def test_event_logging_repository_wo_collection(mongodb_client, logs_database_name):
    with pytest.raises(ValueError):
        EventLoggingRepository(mongodb_client=mongodb_client, database_name=logs_database_name, collection_name='')

