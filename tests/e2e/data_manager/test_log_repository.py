from ted_sws.data_manager.adapters.log_repository import LogRepository
from ted_sws.event_manager.model.message import DBProcessLog as Log

TEST_DATABASE_NAME = "test_logs_database_name"


def test_log_repository_add(mongodb_client):
    mongodb_client.drop_database(TEST_DATABASE_NAME)
    log_repository = LogRepository(database_name=TEST_DATABASE_NAME)
    log = Log(payload={}, name="TEST", message="TEST_LOG")
    log_repository.add(log)
    result: Log = log_repository.create_log_from_dict(log_repository.collection.find_one())
    assert result
    assert result.name == "TEST"
    assert result.message == "TEST_LOG"
    mongodb_client.drop_database(TEST_DATABASE_NAME)
