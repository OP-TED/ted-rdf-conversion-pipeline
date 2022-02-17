import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI


@pytest.fixture
def ted_document_search():
    return TedAPIAdapter(request_api=TedRequestAPI())
