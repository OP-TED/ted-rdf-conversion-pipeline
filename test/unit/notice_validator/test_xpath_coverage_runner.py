from src.ted_sws.core.model.validation_report import ReportNotice
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingPackageRepositoryInFileSystem, \
    MappingPackageRepositoryMongoDB
from src.ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_package_processor_load_package_in_mongo_db
from src.ted_sws.notice_validator.services.xpath_coverage_runner import validate_xpath_coverage_notices, \
    xpath_coverage_json_report, xpath_coverage_html_report, validate_xpath_coverage_notice


def test_xpath_coverage_runner(fake_notice_F03, fake_mapping_package_F03_id, fake_mapping_package_F03_id_with_version,
                               mongodb_client, fake_repository_path, fake_mapping_package_F03_path):
    report_notices = [ReportNotice(notice=fake_notice_F03)]
    mapping_package_repository = MappingPackageRepositoryInFileSystem(repository_path=fake_repository_path)
    mapping_package = mapping_package_repository.get(reference=fake_mapping_package_F03_id)
    report = validate_xpath_coverage_notices(report_notices, mapping_package)
    json_report = xpath_coverage_json_report(report)
    assert isinstance(json_report, dict)
    assert "mapping_package_identifier" in json_report
    assert "validation_result" in json_report
    assert "xpath_assertions" in json_report["validation_result"]
    assert "xpath_covered" in json_report["validation_result"]

    assert xpath_coverage_html_report(report)

    mapping_package_processor_load_package_in_mongo_db(mapping_package_path=fake_mapping_package_F03_path,
                                                     mongodb_client=mongodb_client)
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package = mapping_package_repository.get(reference=fake_mapping_package_F03_id_with_version)
    assert mapping_package

    report = validate_xpath_coverage_notices(report_notices, mapping_package)
    json_report = xpath_coverage_json_report(report)
    assert isinstance(json_report, dict)


def test_validate_xpath_coverage_notice(fake_mapping_package_F03_id, fake_repository_path, fake_notice_F03):
    mapping_package_repository_fs = MappingPackageRepositoryInFileSystem(repository_path=fake_repository_path)
    mapping_package = mapping_package_repository_fs.get(fake_mapping_package_F03_id)

    validate_xpath_coverage_notice(
        notice=fake_notice_F03,
        mapping_package=mapping_package)
