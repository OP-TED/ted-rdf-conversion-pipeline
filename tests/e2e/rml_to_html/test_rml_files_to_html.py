import pytest

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner
from ted_sws.rml_to_html.resources.query_registry import QueryRegistry
from ted_sws.rml_to_html.services.rml_to_html import rml_files_to_html_report, query_uri_substitution, get_query_results


def test_query_uri_substitution():
    query = QueryRegistry().SUBJECT_MAP
    uri = "http://data.europa.eu/a4g/mapping/sf-rml/ResultNotice"
    substituted_query = query_uri_substitution(query=query,
                                               triple_map_uri=uri)
    assert uri in substituted_query


def test_get_query_results(rml_file):
    query = QueryRegistry().TRIPLE_MAP
    results = get_query_results(query=query, sparql_runner=SPARQLRunner(files=[rml_file]))
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, dict)
        assert "type", "value" in result.keys()


def test_rml_files_to_html_report(file_system_repository_path):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=file_system_repository_path)
    html_report = rml_files_to_html_report(mapping_suite_identifier="test_package",
                                           mapping_suite_repository=mapping_suite_repository)

    assert isinstance(html_report, str)
    assert "Logical Source" in html_report
    assert "Subject map" in html_report
    assert "Predicate object maps" in html_report

    with pytest.raises(ValueError):
        rml_files_to_html_report(mapping_suite_identifier="no_package",
                                 mapping_suite_repository=mapping_suite_repository)
