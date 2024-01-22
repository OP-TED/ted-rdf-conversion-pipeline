from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from ted_sws.notice_metadata_processor.services.notice_eligibility import check_package, \
    notice_eligibility_checker, notice_eligibility_checker_by_id


def test_non_eligibility_by_notice(notice_eligibility_repository_path, indexed_notice):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=notice_eligibility_repository_path)
    normalise_notice(notice=indexed_notice)
    notice_eligibility_checker(notice=indexed_notice, mapping_suite_repository=mapping_suite_repository)
    assert indexed_notice.status == NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION


def test_eligibility_by_notice(notice_eligibility_repository_path, notice_2020):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=notice_eligibility_repository_path)
    normalise_notice(notice=notice_2020)
    notice_checker = notice_eligibility_checker(notice=notice_2020, mapping_suite_repository=mapping_suite_repository)
    notice_id, mapping_suite_identifier = notice_checker
    assert notice_id == "408313-2020"
    assert mapping_suite_identifier == "test_package2_v2.1.6"
    assert notice_2020.status == NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION


def test_eligibility_by_notice_id(notice_eligibility_repository_path, notice_2020, notice_repository):
    normalise_notice(notice=notice_2020)
    notice_repository.add(notice_2020)
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=notice_eligibility_repository_path)
    notice_checker = notice_eligibility_checker_by_id(notice_id="408313-2020",
                                                      mapping_suite_repository=mapping_suite_repository,
                                                      notice_repository=notice_repository)
    notice_id, mapping_suite_identifier = notice_checker

    assert notice_id == "408313-2020"
    assert mapping_suite_identifier == "test_package2_v2.1.6"
    assert notice_2020.status == NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION


def test_check_mapping_suite(notice_eligibility_repository_path, normalised_metadata_object):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=notice_eligibility_repository_path)
    is_valid = check_package(mapping_suite=mapping_suite_repository.get("test_package"),
                             notice_metadata=normalised_metadata_object)

    assert isinstance(is_valid, bool)
    assert is_valid

    normalised_metadata_object.eforms_subtype = "15.1"
    is_valid = check_package(mapping_suite=mapping_suite_repository.get("test_package"),
                             notice_metadata=normalised_metadata_object)
    assert is_valid

    normalised_metadata_object.eforms_subtype = "88"
    is_valid = check_package(mapping_suite=mapping_suite_repository.get("test_package"),
                             notice_metadata=normalised_metadata_object)
    assert not is_valid