import pytest
import mongomock
import pymongo

from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository


@pytest.fixture
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    mongo_client = pymongo.MongoClient('server.example.com')
    for database_name in mongo_client.list_database_names():
        mongo_client.drop_database(database_name)
    return mongo_client


@pytest.fixture
def daily_supra_notice_repository(mongodb_client) -> DailySupraNoticeRepository:
    return DailySupraNoticeRepository(mongodb_client=mongodb_client)
