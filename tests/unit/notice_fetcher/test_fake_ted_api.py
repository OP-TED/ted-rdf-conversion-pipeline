import datetime

from tests.fakes.fake_ted_api import FakeTedDocumentSearch


def test_fake_ted_api():
    fake_document_search = FakeTedDocumentSearch()

    get_by_date = fake_document_search.get_by_range_date(start_date=datetime.date(2020, 1, 1),
                                                         end_date=datetime.date(2020, 1, 2))
    get_by_query = fake_document_search.get_by_query(query={"q": "PD=[]"})
    assert isinstance(get_by_date, list)
    assert len(get_by_date) == 1
    assert len(get_by_query) == 1
    assert isinstance(get_by_query, list)
    assert fake_document_search.get_by_id(document_id="ID")
    assert isinstance(fake_document_search.get_by_id(document_id="ID"), dict)
