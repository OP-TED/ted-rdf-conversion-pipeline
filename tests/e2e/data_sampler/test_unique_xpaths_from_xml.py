from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_selectors import get_notice_ids_by_form_number, \
    get_notice_ids_by_eforms_subtype
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice, index_notice_by_id, \
    get_unique_xpaths_from_notice_repository, get_unique_notice_id_from_notice_repository, \
    get_minimal_set_of_notices_for_coverage_xpaths, get_minimal_set_of_xpaths_for_coverage_notices, \
    get_unique_notices_id_covered_by_xpaths, get_unique_xpaths_covered_by_notices, get_most_representative_notices


def test_index_notice(notice_2016):
    result_notice = index_notice(notice=notice_2016)
    assert len(result_notice.xml_metadata.unique_xpaths) == 112


def test_index_notice_by_id(notice_2016, mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=notice_2016)
    index_notice_by_id(notice_id=notice_2016.ted_id, mongodb_client=mongodb_client)
    result_notice = notice_repository.get(reference=notice_2016.ted_id)
    assert len(result_notice.xml_metadata.unique_xpaths) == 112


def test_unique_xpaths_from_xml(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_xpaths = get_unique_xpaths_from_notice_repository(mongodb_client=mongodb_client)
    assert len(unique_xpaths) == 378


def test_unique_notice_id(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_notice_id = get_unique_notice_id_from_notice_repository(mongodb_client=mongodb_client)
    assert len(unique_notice_id) == 82


def test_minimal_set_of_notices_for_coverage_xpaths(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_xpaths = get_unique_xpaths_from_notice_repository(mongodb_client=mongodb_client)
    minimal_set_of_notices = get_minimal_set_of_notices_for_coverage_xpaths(xpaths=unique_xpaths,
                                                                            mongodb_client=mongodb_client)
    assert len(minimal_set_of_notices) == 16


def test_minimal_set_of_xpaths_for_coverage_notices(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_notice_ids = get_unique_notice_id_from_notice_repository(mongodb_client=mongodb_client)
    minimal_set_of_xpaths = get_minimal_set_of_xpaths_for_coverage_notices(notice_ids=unique_notice_ids,
                                                                           mongodb_client=mongodb_client)
    assert len(minimal_set_of_xpaths) == 1


def test_unique_notices_id_covered_by_xpaths(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_xpaths = get_unique_xpaths_from_notice_repository(mongodb_client=mongodb_client)
    unique_notices = get_unique_notices_id_covered_by_xpaths(xpaths=unique_xpaths, mongodb_client=mongodb_client)
    assert len(unique_notices) == 82


def test_unique_xpaths_covered_by_notices(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_notices = get_unique_notice_id_from_notice_repository(mongodb_client=mongodb_client)
    unique_xpaths = get_unique_xpaths_covered_by_notices(notice_ids=unique_notices, mongodb_client=mongodb_client)
    assert len(unique_xpaths) == 378


def test_get_most_representative_notices(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    unique_notices = get_unique_notice_id_from_notice_repository(mongodb_client=mongodb_client)
    most_representative_notices = get_most_representative_notices(notice_ids=unique_notices,
                                                                  mongodb_client=mongodb_client,
                                                                  top_k=10)
    assert most_representative_notices
    assert len(most_representative_notices) == 10


def test_get_most_representative_notices_by_query_result(notice_repository_with_indexed_notices):
    mongodb_client = notice_repository_with_indexed_notices.mongodb_client
    notices_with_form_number_f03 = get_notice_ids_by_form_number(form_number="F03", mongodb_client=mongodb_client)
    most_representative_notices = get_most_representative_notices(notice_ids=notices_with_form_number_f03,
                                                                  mongodb_client=mongodb_client,
                                                                  top_k=10)
    assert most_representative_notices
    assert len(most_representative_notices) == 10

    notices_with_eforms_subtype = get_notice_ids_by_eforms_subtype(eforms_subtype="29", mongodb_client=mongodb_client)
    most_representative_notices = get_most_representative_notices(notice_ids=notices_with_eforms_subtype,
                                                                  mongodb_client=mongodb_client,
                                                                  top_k=10)
    assert most_representative_notices
    assert len(most_representative_notices) == 10



