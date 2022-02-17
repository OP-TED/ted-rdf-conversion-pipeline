import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from tests.fakes.fake_repository import FakeNoticeRepository


@pytest.fixture
def notice_repository():
    return FakeNoticeRepository()

@pytest.fixture
def ted_document_search():
    return TedAPIAdapter(request_api=TedRequestAPI())