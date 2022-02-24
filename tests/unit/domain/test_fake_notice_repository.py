import datetime

from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from tests.fakes.fake_repository import FakeNoticeRepository


def test_fake_notice_repository(ted_document_search):
    fake_notice_repository = FakeNoticeRepository()
    NoticeFetcher(notice_repository=fake_notice_repository,
                            ted_api_adapter=ted_document_search).fetch_notices_by_date_range(
        start_date=datetime.date(2022, 2, 3), end_date=datetime.date(2022, 2, 3))
    notices = [fake_notice_repository.get(reference=reference) for reference in fake_notice_repository.list()]
    for notice in notices:
        fake_notice_repository.add(notice)
    for notice in notices:
        extracted_notice = fake_notice_repository.get(reference=notice.ted_id)
        assert extracted_notice
        assert extracted_notice == notice
    extracted_notice = fake_notice_repository.get(reference="INVALID_REFERENCE")
    assert extracted_notice is None

    extracted_notice_references = fake_notice_repository.list()
    for notice in notices:
        assert notice.ted_id in extracted_notice_references
