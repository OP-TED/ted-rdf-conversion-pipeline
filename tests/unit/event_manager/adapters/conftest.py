import logging
import pytest

from ted_sws.event_manager.adapters.log.logger_mongo_handler import BufferedMongoHandler, MongoHandler


@pytest.fixture
def mongo_handler(mongodb_client):
    return MongoHandler(mongodb_client=mongodb_client)


@pytest.fixture
def buffered_mongo_handler(mongodb_client):
    return BufferedMongoHandler(mongodb_client=mongodb_client)


@pytest.fixture
def mongo_database_name():
    return "test_logs_db"


@pytest.fixture
def mongo_collection_name():
    return "logs_test"


@pytest.fixture
def logger():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    return logger
