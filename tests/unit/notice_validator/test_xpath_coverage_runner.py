import pytest

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_load_package_in_mongo_db
from ted_sws.notice_validator.services.xpath_coverage_runner import coverage_notice_xpath_report, \
    xpath_coverage_json_report, xpath_coverage_html_report, validate_xpath_coverage_notice_by_id
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository


def test_xpath_coverage_runner(fake_notice_F03, fake_conceptual_mappings_F03_path,
                               fake_mapping_suite_F03_id, fake_mapping_suite_F03_id_with_version, mongodb_client,
                               fake_mapping_suite_F03_path, invalid_mapping_suite_id):
    report = coverage_notice_xpath_report([fake_notice_F03], fake_mapping_suite_F03_id,
                                          fake_conceptual_mappings_F03_path, None)
    json_report = xpath_coverage_json_report(report)
    assert isinstance(json_report, dict)
    assert "mapping_suite_identifier" in json_report
    assert "validation_result" in json_report
    assert "xpath_assertions" in json_report["validation_result"]

    assert xpath_coverage_html_report(report)

    mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=fake_mapping_suite_F03_path,
                                                     mongodb_client=mongodb_client)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite_F03_id_with_version)
    assert mapping_suite

    report = coverage_notice_xpath_report([fake_notice_F03], fake_mapping_suite_F03_id_with_version,
                                          fake_conceptual_mappings_F03_path, None, mongodb_client)
    json_report = xpath_coverage_json_report(report)
    assert isinstance(json_report, dict)

    with pytest.raises(ValueError):
        coverage_notice_xpath_report([fake_notice_F03], invalid_mapping_suite_id, None, None, mongodb_client)


def test_validate_xpath_coverage_notice_by_id(fake_notice_id, fake_mapping_suite_F03_id, mongodb_client,
                                              fake_repository_path, fake_notice_F03_content, fake_notice_F03,
                                              fake_mapping_suite_F03_id_with_version):
    mapping_suite_repository_fs = MappingSuiteRepositoryInFileSystem(repository_path=fake_repository_path)
    mapping_suite = mapping_suite_repository_fs.get(fake_mapping_suite_F03_id)
    mapping_suite_repository_db = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)

    with pytest.raises(ValueError):
        validate_xpath_coverage_notice_by_id(
            notice_id=fake_notice_id,
            mapping_suite_identifier=fake_mapping_suite_F03_id,
            mapping_suite_repository=mapping_suite_repository_db,
            mongodb_client=mongodb_client,
            with_html=True)

    notice_repository.add(fake_notice_F03)

    with pytest.raises(ValueError):
        validate_xpath_coverage_notice_by_id(
            notice_id=fake_notice_id,
            mapping_suite_identifier=fake_mapping_suite_F03_id,
            mapping_suite_repository=mapping_suite_repository_db,
            mongodb_client=mongodb_client)

    mapping_suite_repository_db.add(mapping_suite)

    validate_xpath_coverage_notice_by_id(
        notice_id=fake_notice_id,
        mapping_suite_identifier=fake_mapping_suite_F03_id_with_version,
        mapping_suite_repository=mapping_suite_repository_db,
        mongodb_client=mongodb_client)
