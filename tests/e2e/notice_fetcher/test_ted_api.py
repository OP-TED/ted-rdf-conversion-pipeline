import datetime

import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI


def test_ted_api():
    ted = TedAPIAdapter(request_api=TedRequestAPI())
    xml_text = "<NOTICE_DATA>"

    notice_by_id = ted.get_by_id(document_id="67623-2022")
    notice_by_date = ted.get_by_range_date(start_date=datetime.date(2022, 2, 3), end_date=datetime.date(2022, 2, 3))
    notice_by_date_wildcard = ted.get_by_wildcard_date(wildcard_date="20220203*")
    notice_by_query = ted.get_by_query(query={"q": "ND=[67623-2022]"})

    assert xml_text in notice_by_id["content"]
    assert isinstance(notice_by_id, dict)
    assert len(notice_by_date) == 95
    assert len(notice_by_date_wildcard) == 95
    assert isinstance(notice_by_date, list)
    assert isinstance(notice_by_date_wildcard, list)
    assert isinstance(notice_by_query, list)
    assert isinstance(notice_by_date[0], dict)
    assert isinstance(notice_by_date_wildcard[0], dict)
    assert isinstance(notice_by_query[0], dict)
    assert len(notice_by_query) == 1


def test_ted_api_error():
    ted = TedAPIAdapter(request_api=TedRequestAPI())
    with pytest.raises(Exception) as e:
        ted.get_by_query(query={"q": "NDE=67623-2022"})
    assert str(e.value) == "The API call failed with: <Response [500]>"
