import pytest
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_fetcher.adapters.ted_api import DEFAULT_TED_API_URL


NOTICE_STORAGE_FEATURES_TEST_DB = "features_test_db_for_notice"

@pytest.fixture
def notice_storage():
    url = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(url)
    mongodb_client.drop_database(NOTICE_STORAGE_FEATURES_TEST_DB)
    return NoticeRepository(mongodb_client=mongodb_client, database_name=NOTICE_STORAGE_FEATURES_TEST_DB)


@pytest.fixture
def notice_identifier():
    return "067623-2022"


@pytest.fixture
def notice_search_query():
    return {"q": "ND=[067623-2022]"}


@pytest.fixture
def notice_incorrect_search_query():
    return {"q": "ND=067623-20224856"}


@pytest.fixture
def api_end_point():
    return DEFAULT_TED_API_URL
