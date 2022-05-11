import pytest
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db


@pytest.fixture
def mongodb_client():
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    protected_databases = ['admin', 'config', 'local']
    existing_databases = mongodb_client.list_database_names()
    databases_to_delete = list(set(existing_databases) - set(protected_databases))
    for database in databases_to_delete:
        mongodb_client.drop_database(database)
    return mongodb_client

@pytest.fixture
def notice_repository_with_indexed_notices(mongodb_client) -> NoticeRepository:

    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(
        mapping_suite_package_name="package_F03_test",
        mongodb_client=mongodb_client,
        load_test_data=True
    )
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice in notice_repository.list():
        indexed_notice = index_notice(notice=notice)
        notice_repository.update(notice=indexed_notice)
    return notice_repository
