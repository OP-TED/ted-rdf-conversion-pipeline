import datetime
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


def test_notice_fetcher_by_identifier(notice_repository, ted_document_search):
    document_id = "067623-2022"
    NoticeFetcher(notice_repository=notice_repository, ted_api_adapter=ted_document_search).fetch_notice_by_id(document_id=document_id)
    notice = notice_repository.get(reference=document_id)
    assert isinstance(notice, Notice)
    assert notice
    assert notice.original_metadata
    assert notice.ted_id
    assert notice.ted_id == document_id
    assert notice.xml_manifestation
    assert notice.status == NoticeStatus.RAW


def test_notice_fetcher_by_search_query(notice_repository, ted_document_search):
    query = {"q": "ND=[67623-2022]"}
    NoticeFetcher(notice_repository=notice_repository, ted_api_adapter=ted_document_search).fetch_notices_by_query(
        query=query)
    notices = list(notice_repository.list())
    assert isinstance(notices, list)
    assert len(notices) == 1
    assert isinstance(notices[0], Notice)


def test_notice_fetcher_by_date_range(notice_repository, ted_document_search):
    NoticeFetcher(notice_repository=notice_repository, ted_api_adapter=ted_document_search).fetch_notices_by_date_range(
        start_date=datetime.date(2022, 2, 3), end_date=datetime.date(2022, 2, 3))
    notices = list(notice_repository.list())
    xml_text = "<NOTICE_DATA>"

    assert isinstance(notices, list)
    assert len(notices) == 1
    assert isinstance(notices[0], Notice)
    assert xml_text in notices[0].xml_manifestation.object_data


def test_notice_fetcher_by_date_wild_card(notice_repository, ted_document_search):
    NoticeFetcher(notice_repository=notice_repository,ted_api_adapter=ted_document_search).fetch_notices_by_date_wild_card(
        wildcard_date="20220203*")
    notices = list(notice_repository.list())
    xml_text = "<NOTICE_DATA>"

    assert isinstance(notices, list)
    assert len(notices) == 1
    assert isinstance(notices[0], Notice)
    assert xml_text in notices[0].xml_manifestation.object_data
