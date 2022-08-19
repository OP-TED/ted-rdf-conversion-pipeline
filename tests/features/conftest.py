import mongomock
import pymongo
import pytest

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository

NOTICE_STORAGE_FEATURES_TEST_DB = "features_test_db_for_notice"


@pytest.fixture
def mongodb_end_point():
    return config.MONGO_DB_AUTH_URL


@pytest.fixture
def mongodb_client(mongodb_end_point):
    return pymongo.MongoClient(mongodb_end_point)


@pytest.fixture
def ted_api_end_point():
    return config.TED_API_URL


@pytest.fixture
def notice_repository(mongodb_client):
    return NoticeRepository(mongodb_client=mongodb_client, database_name=NOTICE_STORAGE_FEATURES_TEST_DB)
