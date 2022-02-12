from datetime import date

from ted_sws.notice_fetcher.adapters.ted_api import TedDocumentSearch
from tests.fakes.fake_ted_api import FakeRequestAPI


def test_ted_api():
    fake_ted = TedDocumentSearch(request_api=FakeRequestAPI())
    xml_text = "<NOTICE_DATA>"
    notice_by_id = fake_ted.get_by_id(document_id="67623-2023")
    notice_by_date = fake_ted.get_by_range_date(start_date=date(2022, 2, 3), end_date=date(2022, 2, 3))
    notice_by_date_wildcard = fake_ted.get_by_wildcard_date(wildcard_date="20220203*")
    notice_by_query = fake_ted.get_by_query(query={"q": "ND=[67623-2023]"})

    assert xml_text in notice_by_id["content"]
    assert isinstance(notice_by_id, dict)
    assert len(notice_by_date) == 2
    assert len(notice_by_date_wildcard) == 2
    assert isinstance(notice_by_date, list)
    assert isinstance(notice_by_date_wildcard, list)
    assert isinstance(notice_by_query, list)
    assert isinstance(notice_by_date[0], dict)
    assert isinstance(notice_by_date_wildcard[0], dict)
    assert isinstance(notice_by_query[0], dict)
    assert len(notice_by_query) == 2