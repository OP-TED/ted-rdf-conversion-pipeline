from pymongo import DESCENDING

from ted_sws.event_manager.adapters.log_repository import LogRepository
from ted_sws.event_manager.model.message import DBProcessLog as Log
from bson import ObjectId


def test_create_dict_from_log(db_process_log):
    log_dict = LogRepository.create_dict_from_log(db_process_log)
    assert log_dict
    assert 'request' in log_dict
    assert 'POSITIONAL_OR_KEYWORD' in log_dict['request']


def test_create_log_from_dict(db_process_log_dict):
    db_process_log_dict['_id'] = "FAKE_ID"
    log = LogRepository.create_log_from_dict(db_process_log_dict)
    assert log
    assert log.name == "TEST"
    assert log.message == "TEST_LOG"


def test_log_repository_add(mongodb_client, db_process_log):
    mongodb_client.drop_database(LogRepository._database_name)
    log_repository = LogRepository(mongodb_client=mongodb_client)
    log_repository.add(db_process_log)
    result: Log = LogRepository.create_log_from_dict(
        log_repository.collection.find_one({}, sort=[('created_at', DESCENDING)]))
    assert result
    assert result.name == "TEST"
    assert result.message == "TEST_LOG"
    mongodb_client.drop_database(LogRepository._database_name)


def test_log_repository_update(mongodb_client, db_process_log):
    mongodb_client.drop_database(LogRepository._database_name)
    log_repository = LogRepository(mongodb_client=mongodb_client)
    _id = log_repository.add(db_process_log)
    result: Log = LogRepository.create_log_from_dict(
        log_repository.collection.find_one({}, sort=[('created_at', DESCENDING)]))
    assert result
    assert result.name != "UPDATED_TEST"

    db_process_log.name = "UPDATED_TEST"
    log_repository.update(_id, db_process_log)
    result: Log = LogRepository.create_log_from_dict(
        log_repository.collection.find_one({"_id": ObjectId(_id)}))
    assert result
    assert result.name == "UPDATED_TEST"

    mongodb_client.drop_database(LogRepository._database_name)
