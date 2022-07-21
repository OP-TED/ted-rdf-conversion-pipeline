from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_notice_into_triple_store
from tests.fakes.fake_repository import FakeNoticeRepository


def test_load_notice_into_triple_store(transformed_complete_notice, allegro_triple_store):
    fake_notice_repo = FakeNoticeRepository()
    fake_notice_repo.add(transformed_complete_notice)

    load_notice_into_triple_store(notice_id=transformed_complete_notice.ted_id, notice_repository=fake_notice_repo,
                                  triple_store_repository=allegro_triple_store)

    assert True

