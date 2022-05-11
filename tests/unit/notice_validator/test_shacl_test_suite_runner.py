import pytest

from ted_sws.core.model.manifestation import RDFManifestation, RDFValidationManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_validator.model.shacl_test_suite import SHACLSuiteValidationReport
from ted_sws.notice_validator.services.shacl_test_suite_runner import SHACLTestSuiteRunner, SHACLReportBuilder, \
    validate_notice_with_shacl_suite, validate_notice_by_id_with_shacl_suite


def test_sparql_query_test_suite_runner(rdf_file_content, shacl_test_suite, dummy_mapping_suite):
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation, shacl_test_suite=shacl_test_suite,
                                         mapping_suite=dummy_mapping_suite)

    test_suite_execution = sparql_runner.execute_test_suite()
    assert isinstance(test_suite_execution, SHACLSuiteValidationReport)
    assert isinstance(test_suite_execution.validation_result.results_dict, dict)


def test_sparql_query_test_suite_runner_error(rdf_file_content, dummy_mapping_suite, bad_shacl_test_suite):
    dummy_mapping_suite.shacl_test_suites = [bad_shacl_test_suite]
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation, shacl_test_suite=bad_shacl_test_suite,
                                         mapping_suite=dummy_mapping_suite)

    test_suite_execution = sparql_runner.execute_test_suite()
    assert isinstance(test_suite_execution, SHACLSuiteValidationReport)
    assert test_suite_execution.validation_result.error

def test_shacl_report_builder(rdf_file_content, shacl_test_suite, dummy_mapping_suite):
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation, shacl_test_suite=shacl_test_suite,
                                         mapping_suite=dummy_mapping_suite)
    report_builder = SHACLReportBuilder(shacl_test_suite_execution=sparql_runner.execute_test_suite())

    reports = report_builder.generate_reports()
    assert isinstance(reports, RDFValidationManifestation)
    assert reports.object_data
    assert "shacl_test_package" in reports.object_data
    assert reports.shacl_test_suite_identifier == "shacl_test_package"


def test_validate_notice_with_shacl_suite(notice_with_distilled_status, dummy_mapping_suite, rdf_file_content):
    notice = notice_with_distilled_status
    validate_notice_with_shacl_suite(notice=notice, mapping_suite_package=dummy_mapping_suite)

    assert notice.status == NoticeStatus.VALIDATED
    assert isinstance(notice.get_rdf_validation(), list)
    assert len(notice.get_rdf_validation()) == 1
    assert isinstance(notice.get_rdf_validation()[0], RDFValidationManifestation)
    assert notice.get_rdf_validation()[0].object_data
    assert notice.get_rdf_validation()[0].validation_result


def test_validate_notice_by_id_with_shacl_suite(notice_with_distilled_status, rdf_file_content, notice_repository,
                                                path_to_file_system_repository):
    notice = notice_with_distilled_status
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=path_to_file_system_repository)
    notice_repository.add(notice)

    validate_notice_by_id_with_shacl_suite(notice_id="408313-2020",
                                           mapping_suite_repository=mapping_suite_repository,
                                           notice_repository=notice_repository,
                                           mapping_suite_identifier="test_package")

    assert notice.status == NoticeStatus.VALIDATED
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
