import pytest
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.metadata import XMLMetadata
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository

from ted_sws.notice_fetcher.adapters.ted_api import DEFAULT_TED_API_URL, TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from tests import TEST_DATA_PATH

NOTICE_STORAGE_FEATURES_TEST_DB = "features_test_db_for_notice"


@pytest.fixture
def api_end_point():
    return DEFAULT_TED_API_URL


@pytest.fixture
def notice_storage():
    url = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(url)
    mongodb_client.drop_database(NOTICE_STORAGE_FEATURES_TEST_DB)
    return NoticeRepository(mongodb_client=mongodb_client, database_name=NOTICE_STORAGE_FEATURES_TEST_DB)


@pytest.fixture
def f03_notice_2020(notice_storage, api_end_point):
    notice_search_query = {"q": "ND=[408313-2020]"}
    NoticeFetcher(notice_repository=notice_storage,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(),
                                                ted_api_url=api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    notice = notice_storage.get(reference="408313-2020")
    notice.set_xml_metadata(xml_metadata=XMLMetadata(unique_xpaths=["FAKE_INDEX_XPATHS"]))
    return notice


@pytest.fixture
def f18_notice_2022(notice_storage, api_end_point):
    notice_search_query = {"q": "ND=[067623-2022]"}
    NoticeFetcher(notice_repository=notice_storage,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(),
                                                ted_api_url=api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    notice = notice_storage.get(reference="067623-2022")
    notice.set_xml_metadata(xml_metadata=XMLMetadata(unique_xpaths=["FAKE_INDEX_XPATHS"]))
    return notice


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def mapping_suite_repository_in_file_system(file_system_repository_path):
    return MappingSuiteRepositoryInFileSystem(repository_path=file_system_repository_path)
