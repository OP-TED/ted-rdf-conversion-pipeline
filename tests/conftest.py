import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter
from tests.fakes.fake_ted_api import FakeRequestAPI



@pytest.fixture
def ted_document_search():
    return TedAPIAdapter(request_api=FakeRequestAPI())