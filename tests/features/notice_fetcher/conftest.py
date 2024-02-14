from datetime import date

import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from tests.fakes.fake_ted_api import FakeTedApiAdapter, FakeRequestAPI


@pytest.fixture
def fetch_notice_id():
    return "67623-2022"


@pytest.fixture
def fetch_start_date():
    return date(2020, 2, 3)


@pytest.fixture
def fetch_date(fetch_start_date):
    return fetch_start_date


@pytest.fixture
def fetch_end_date():
    return date(2020, 2, 3)


@pytest.fixture
def fetch_wildcard_date():
    return "20200203*"


@pytest.fixture
def fetch_query(fetch_wildcard_date):
    return {"query": f"PD={fetch_wildcard_date}"}


@pytest.fixture
def notice_fetcher(notice_repository, ted_api_end_point):
    return NoticeFetcher(notice_repository=notice_repository,
                         ted_api_adapter=TedAPIAdapter(FakeRequestAPI()))
