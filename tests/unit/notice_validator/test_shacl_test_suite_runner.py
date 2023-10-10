import pytest

from ted_sws.core.model.manifestation import RDFManifestation, RDFValidationManifestation, \
    SHACLTestSuiteValidationReport
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.core.model.validation_report import ReportNotice, SHACLValidationSummaryReport
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_validator.services.shacl_test_suite_runner import SHACLTestSuiteRunner, \
    validate_notice_with_shacl_suite, validate_notice_by_id_with_shacl_suite, generate_shacl_report, \
    generate_shacl_validation_summary_report


def test_sparql_query_test_suite_runner(rdf_file_content, shacl_test_suite, dummy_mapping_suite):
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation, shacl_test_suite=shacl_test_suite,
                                         mapping_suite=dummy_mapping_suite)

    test_suite_execution = sparql_runner.execute_test_suite()
    assert isinstance(test_suite_execution, SHACLTestSuiteValidationReport)
    assert isinstance(test_suite_execution.validation_results.results_dict, dict)


def test_sparql_query_test_suite_runner_error(rdf_file_content, dummy_mapping_suite, bad_shacl_test_suite):
    dummy_mapping_suite.shacl_test_suites = [bad_shacl_test_suite]
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation, shacl_test_suite=bad_shacl_test_suite,
                                         mapping_suite=dummy_mapping_suite)

    test_suite_execution = sparql_runner.execute_test_suite()
    assert isinstance(test_suite_execution, SHACLTestSuiteValidationReport)
    assert test_suite_execution.validation_results.error


def test_shacl_report_builder(rdf_file_content, shacl_test_suite, dummy_mapping_suite):
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation, shacl_test_suite=shacl_test_suite,
                                         mapping_suite=dummy_mapping_suite)
    report = generate_shacl_report(shacl_test_suite_execution=sparql_runner.execute_test_suite(), with_html=True)
    assert isinstance(report, RDFValidationManifestation)
    assert report.object_data
    assert "shacl_test_package" in report.object_data
    assert report.test_suite_identifier == "shacl_test_package"


def test_validate_notice_with_shacl_suite(notice_with_distilled_status, dummy_mapping_suite, rdf_file_content):
    notice = notice_with_distilled_status
    assert notice.rdf_manifestation
    assert notice.distilled_rdf_manifestation
    validate_notice_with_shacl_suite(notice=notice, mapping_suite_package=dummy_mapping_suite)
    rdf_validation = notice.get_rdf_validation()
    distilled_rdf_validation = notice.get_distilled_rdf_validation()
    assert notice.status == NoticeStatus.DISTILLED
    assert isinstance(rdf_validation, list)
    assert len(rdf_validation) == 1
    assert isinstance(rdf_validation[0], RDFValidationManifestation)
    assert rdf_validation[0].object_data
    assert rdf_validation[0].validation_results
    assert isinstance(distilled_rdf_validation, list)
    assert len(distilled_rdf_validation) == 1
    assert isinstance(distilled_rdf_validation[0], RDFValidationManifestation)
    assert distilled_rdf_validation[0].object_data
    assert distilled_rdf_validation[0].validation_results


def test_validate_notice_by_id_with_shacl_suite(notice_with_distilled_status, rdf_file_content, notice_repository,
                                                path_to_file_system_repository):
    notice = notice_with_distilled_status
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=path_to_file_system_repository)
    notice_repository.add(notice)

    assert len(notice.get_rdf_validation()) == 0
    validate_notice_by_id_with_shacl_suite(notice_id="408313-2020",
                                           mapping_suite_repository=mapping_suite_repository,
                                           notice_repository=notice_repository,
                                           mapping_suite_identifier="test_package")

    assert notice.status == NoticeStatus.DISTILLED
    assert isinstance(notice.get_rdf_validation(), list)
    assert len(notice.get_rdf_validation()) == 1
    assert isinstance(notice.get_rdf_validation()[0], RDFValidationManifestation)
    assert notice.get_rdf_validation()[0].object_data

    with pytest.raises(ValueError):
        validate_notice_by_id_with_shacl_suite(notice_id="408313-202085569",
                                               mapping_suite_repository=mapping_suite_repository,
                                               notice_repository=notice_repository,
                                               mapping_suite_identifier="test_package")

    with pytest.raises(ValueError):
        validate_notice_by_id_with_shacl_suite(notice_id="408313-2020",
                                               mapping_suite_repository=mapping_suite_repository,
                                               notice_repository=notice_repository,
                                               mapping_suite_identifier="no_package_here")


def test_generate_shacl_validation_summary_report(notice_with_distilled_status, fake_validation_notice,
                                                  dummy_mapping_suite, rdf_file_content):
    notice = notice_with_distilled_status
    assert notice.rdf_manifestation
    assert notice.distilled_rdf_manifestation
    notice.rdf_manifestation.shacl_validations = fake_validation_notice.rdf_manifestation.shacl_validations
    report_notice: ReportNotice = ReportNotice(notice=notice)
    report: SHACLValidationSummaryReport = generate_shacl_validation_summary_report(
        report_notices=[report_notice],
        mapping_suite_package=dummy_mapping_suite,
        with_html=True
    )
    assert report.object_data
    assert report.notices[0].notice_id == notice.ted_id
    assert report.validation_results
    assert len(report.validation_results) > 0
