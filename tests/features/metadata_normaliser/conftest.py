import pytest

from ted_sws import config
from tests.fakes.fake_repository import FakeNoticeRepository


@pytest.fixture
def notice_identifier():
    return "067623-2022"


@pytest.fixture
def api_end_point():
    return config.TED_API_URL


@pytest.fixture
def fake_notice_storage():
    return FakeNoticeRepository()
