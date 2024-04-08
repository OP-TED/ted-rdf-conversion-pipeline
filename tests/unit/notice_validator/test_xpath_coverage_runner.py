from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_load_package_in_mongo_db
from ted_sws.notice_validator.services.xpath_coverage_runner import validate_xpath_coverage_notices, \
    xpath_coverage_json_report, xpath_coverage_html_report, validate_xpath_coverage_notice


def test_xpath_coverage_runner(fake_notice_F03, fake_mapping_suite_F03_id, fake_mapping_suite_F03_id_with_version,
                               mongodb_client, fake_repository_path, fake_mapping_suite_F03_path):
    report_notices = [ReportNotice(notice=fake_notice_F03)]
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=fake_repository_path)
    mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite_F03_id)
    report = validate_xpath_coverage_notices(report_notices, mapping_suite)
    json_report = xpath_coverage_json_report(report)
    assert isinstance(json_report, dict)
    assert "mapping_suite_identifier" in json_report
    assert "validation_result" in json_report
    assert "xpath_assertions" in json_report["validation_result"]
    assert "xpath_covered" in json_report["validation_result"]

    assert xpath_coverage_html_report(report)

    mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=fake_mapping_suite_F03_path,
                                                     mongodb_client=mongodb_client)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite_F03_id_with_version)
    assert mapping_suite

    report = validate_xpath_coverage_notices(report_notices, mapping_suite)
    json_report = xpath_coverage_json_report(report)
    assert isinstance(json_report, dict)


def test_validate_xpath_coverage_notice(fake_mapping_suite_F03_id, fake_repository_path, fake_notice_F03):
    mapping_suite_repository_fs = MappingSuiteRepositoryInFileSystem(repository_path=fake_repository_path)
    mapping_suite = mapping_suite_repository_fs.get(fake_mapping_suite_F03_id)

    validate_xpath_coverage_notice(
        notice=fake_notice_F03,
        mapping_suite=mapping_suite)
