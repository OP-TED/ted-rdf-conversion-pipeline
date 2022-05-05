import pytest

from ted_sws.core.model.manifestation import RDFManifestation, RDFValidationManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_validator.model.sparql_test_suite import SPARQLQuery, SPARQLQueryResult
from ted_sws.notice_validator.services.sparql_test_suite_runner import SPARQLTestSuiteRunner, SPARQLReportBuilder, \
    validate_notice_with_sparql_suite, validate_notice_by_id_with_sparql_suite, extract_metadata_from_sparql_query


def test_sparql_query_test_suite_runner(rdf_file_content, sparql_test_suite, dummy_mapping_suite, sparql_file_one):
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SPARQLTestSuiteRunner(rdf_manifestation=rdf_manifestation, sparql_test_suite=sparql_test_suite,
                                          mapping_suite=dummy_mapping_suite)

    list_of_file_resources = sparql_test_suite.sparql_tests
    for file in list_of_file_resources:
        query = sparql_runner._sparql_query_from_file_resource(file_resource=file)
        assert isinstance(query, SPARQLQuery)
        assert isinstance(query.query, str)
        assert query.title
        assert query.description
        assert query.query
        assert "this is a description" == query.description

    query_meta = ["# title", "# description"]
    for meta in query_meta:
        assert meta in sparql_file_one.file_content
    sanitized_query = sparql_runner._sanitize_query(sparql_file_one.file_content)
    for meta in query_meta:
        assert meta not in sanitized_query

    test_suite_executions = sparql_runner.execute_test_suite().execution_results
    assert isinstance(test_suite_executions, list)
    for execution in test_suite_executions:
        assert isinstance(execution, SPARQLQueryResult)

    assert test_suite_executions[1].result == "True"
    assert test_suite_executions[0].result == "False"


def test_sparql_query_test_suite_runner_error(sparql_test_suite_with_invalid_query, dummy_mapping_suite,
                                              rdf_file_content):
    sparql_runner = SPARQLTestSuiteRunner(rdf_manifestation=RDFManifestation(object_data=rdf_file_content),
                                          sparql_test_suite=sparql_test_suite_with_invalid_query,
                                          mapping_suite=dummy_mapping_suite).execute_test_suite()
    assert sparql_runner.execution_results[0].error
    assert isinstance(sparql_runner.execution_results[0].error, str)
    assert "Expected" in sparql_runner.execution_results[0].error


def test_sparql_report_builder(rdf_file_content, sparql_test_suite, dummy_mapping_suite):
    rdf_manifestation = RDFManifestation(object_data=rdf_file_content)
    sparql_runner = SPARQLTestSuiteRunner(rdf_manifestation=rdf_manifestation, sparql_test_suite=sparql_test_suite,
                                          mapping_suite=dummy_mapping_suite)
    report_builder = SPARQLReportBuilder(sparql_test_suite_execution=sparql_runner.execute_test_suite())

    json_report = report_builder.generate_json()
    html_report = report_builder.generate_html()

    assert json_report
    assert html_report
    assert isinstance(json_report, RDFValidationManifestation)
    assert isinstance(html_report, RDFValidationManifestation)
    assert json_report.sparql_test_suite_identifier == "sparql_test_package"


def test_validate_notice_with_sparql_suite(notice_with_distilled_status, dummy_mapping_suite, rdf_file_content):
    notice = notice_with_distilled_status
    validate_notice_with_sparql_suite(notice=notice, mapping_suite_package=dummy_mapping_suite)

    assert notice.status == NoticeStatus.VALIDATED
    assert isinstance(notice.get_rdf_validation(), list)
    assert len(notice.get_rdf_validation()) == 2
    assert isinstance(notice.get_rdf_validation()[0], RDFValidationManifestation)
    assert notice.get_rdf_validation()[0].object_data


def test_validate_notice_by_id_with_sparql_suite(notice_with_distilled_status, rdf_file_content, notice_repository,
                                                 path_to_file_system_repository):
    notice = notice_with_distilled_status
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=path_to_file_system_repository)
    notice_repository.add(notice)

    validate_notice_by_id_with_sparql_suite(notice_id="408313-2020",
                                            mapping_suite_repository=mapping_suite_repository,
                                            notice_repository=notice_repository,
                                            mapping_suite_identifier="test_package")

    assert notice.status == NoticeStatus.VALIDATED
    assert isinstance(notice.get_rdf_validation(), list)
    assert len(notice.get_rdf_validation()) == 2
    assert isinstance(notice.get_rdf_validation()[0], RDFValidationManifestation)
    assert notice.get_rdf_validation()[0].object_data

    with pytest.raises(ValueError):
        validate_notice_by_id_with_sparql_suite(notice_id="408313-202085569",
                                                mapping_suite_repository=mapping_suite_repository,
                                                notice_repository=notice_repository,
                                                mapping_suite_identifier="test_package")

    with pytest.raises(ValueError):
        validate_notice_by_id_with_sparql_suite(notice_id="408313-2020",
                                                mapping_suite_repository=mapping_suite_repository,
                                                notice_repository=notice_repository,
                                                mapping_suite_identifier="no_package_here")


def test_get_metadata_from_freaking_sparql_queries(query_content, query_content_without_description,
                                                   query_content_with_xpath):
    metadata = extract_metadata_from_sparql_query(query_content)
    assert metadata["title"]
    assert metadata["description"]
    assert "SELECT" not in metadata

    metadata = extract_metadata_from_sparql_query(query_content_with_xpath)
    assert metadata["title"]
    assert metadata["description"]
    assert metadata["xpath"]
    assert "PREFIX" not in metadata

    metadata = extract_metadata_from_sparql_query(query_content_without_description)
    assert metadata["title"]
    assert "description" not in metadata
