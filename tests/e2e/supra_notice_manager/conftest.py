import pytest
import mongomock
import pymongo

from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository


@pytest.fixture
def daily_supra_notice_repository(fake_mongodb_client) -> DailySupraNoticeRepository:
    return DailySupraNoticeRepository(mongodb_client=fake_mongodb_client)
