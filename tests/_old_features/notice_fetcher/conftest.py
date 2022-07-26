import pytest


@pytest.fixture
def notice_identifier():
    return "067623-2022"


@pytest.fixture
def notice_search_query():
    return {"q": "ND=[067623-2022]"}


@pytest.fixture
def notice_incorrect_search_query():
    return {"q": "ND=067623-20224856"}


