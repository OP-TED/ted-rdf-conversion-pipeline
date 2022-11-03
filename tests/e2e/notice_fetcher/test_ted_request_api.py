import pytest

from ted_sws import config
from ted_sws.notice_fetcher.adapters.ted_api import TedRequestAPI


def test_ted_request_api():
    ted_api_request = TedRequestAPI()
    notice_by_query = ted_api_request(api_url=config.TED_API_URL, api_query={"q": "ND=[67623-2022]"})
    assert notice_by_query
    assert isinstance(notice_by_query, dict)
    with pytest.raises(Exception) as e:
        ted_api_request(api_url=config.TED_API_URL, api_query={"q": "INCORRECT PARAMS"})
    assert str(e.value) == "The API call failed with: <Response [500]>"

