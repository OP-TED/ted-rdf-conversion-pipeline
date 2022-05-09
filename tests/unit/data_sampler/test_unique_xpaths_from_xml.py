from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice, index_notice_by_id, \
    get_unique_xpaths_from_notice_repository, get_unique_notice_id_from_notice_repository


def test_unique_xpaths_from_xml(notice_2016, mongodb_client):
    notice = index_notice(notice=notice_2016)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=notice)
    unique_xpaths = get_unique_xpaths_from_notice_repository(mongodb_client=mongodb_client)
    assert len(unique_xpaths) == 112


def test_unique_notice_id(notice_2016, mongodb_client):
    notice = index_notice(notice=notice_2016)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=notice)
    unique_notice_id = get_unique_notice_id_from_notice_repository(mongodb_client=mongodb_client)
    assert len(unique_notice_id) == 1
