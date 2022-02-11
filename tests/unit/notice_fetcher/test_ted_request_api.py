import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedRequestAPI, DEFAULT_TED_API_URL


def test_ted_request_api():
    ted_api_request = TedRequestAPI()
    with pytest.raises(Exception) as e:
        ted_api_request(api_url=DEFAULT_TED_API_URL, api_query={"q": "INCORRECT PARAMS"})
    assert str(e.value) == "The API call failed with: <Response [500]>"
