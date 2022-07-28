import pytest

from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository
from tests.fakes.fake_ted_api import FakeRequestAPI


@pytest.fixture
def daily_supra_notice_repository(mongodb_client) -> DailySupraNoticeRepository:
    return DailySupraNoticeRepository(mongodb_client=mongodb_client)


@pytest.fixture
def fake_request_api():
    return FakeRequestAPI()
