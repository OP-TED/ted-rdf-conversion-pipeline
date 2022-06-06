import json
from string import Template

from jinja2 import Environment, PackageLoader

from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner
from ted_sws.rml_to_html.resources.query_registry import QueryRegistry

TEMPLATES = Environment(loader=PackageLoader("ted_sws.rml_to_html.resources", "templates"))
RML_TO_HTML_REPORT_TEMPLATE = "rml_to_html_report.jinja2"


def query_uri_substitution(query: str, triple_map_uri: str) -> str:
    """
    Method to replace triple map URI in the SPARQL query
    :param query:
    :param triple_map_uri:
    :return:
    """
    return Template(query).substitute(tripleMapUri=triple_map_uri)


def get_query_results(query: str, sparql_runner: SPARQLRunner) -> dict:
    """
    Method to get query results
    :param query:
    :param sparql_runner:
    :return:
    """
    return json.loads(
        sparql_runner.query(query_object=query).serialize(
            format="json").decode("utf-8"))["results"]["bindings"]


def run_queries_for_triple_map(triple_map_uri: str, query_registry: QueryRegistry, sparql_runner: SPARQLRunner) -> dict:
    """
    Running all queries against a triple map URI
    :param triple_map_uri:
    :param query_registry:
    :param sparql_runner:
    :return:
    """
    return {
        "triple_map_uri": triple_map_uri,
        "details": get_query_results(
            query=query_uri_substitution(query=query_registry.TRIPLE_MAP_COMMENT_LABEL, triple_map_uri=triple_map_uri),
            sparql_runner=sparql_runner),
        "logical_source": get_query_results(
            query=query_uri_substitution(query=query_registry.LOGICAL_SOURCE, triple_map_uri=triple_map_uri),
            sparql_runner=sparql_runner),
        "subject_map": get_query_results(
            query_uri_substitution(query=query_registry.SUBJECT_MAP, triple_map_uri=triple_map_uri),
            sparql_runner=sparql_runner),
        "predicate_object_map": get_query_results(
            query=query_uri_substitution(query=query_registry.PREDICATE_OBJECT_MAP, triple_map_uri=triple_map_uri),
            sparql_runner=sparql_runner)

    }


def rml_files_to_html_report(mapping_suite_identifier: str, mapping_suite_repository: MappingSuiteRepositoryABC):
    """
    Creating an html report from loaded rml files
    :param mapping_suite_identifier:
    :param mapping_suite_repository:
    :return:
    """
    mapping_suite_package = mapping_suite_repository.get(reference=mapping_suite_identifier)
    if mapping_suite_package is None:
        raise ValueError(f'Mapping suite package, with {mapping_suite_identifier} id, was not found')
    rml_files = mapping_suite_package.transformation_rule_set.rml_mapping_rules
    query_registry = QueryRegistry()
    sparql_runner = SPARQLRunner(files=rml_files)

    triple_maps = get_query_results(query=query_registry.TRIPLE_MAP, sparql_runner=sparql_runner)
    triple_maps_uris = [triple_map["tripleMap"]["value"] for triple_map in triple_maps]
    triple_maps_details = {}
    for triple_map_uri in triple_maps_uris:
        triple_maps_details[triple_map_uri] = run_queries_for_triple_map(triple_map_uri=triple_map_uri,
                                                                         query_registry=query_registry,
                                                                         sparql_runner=sparql_runner)

    html_report = TEMPLATES.get_template(RML_TO_HTML_REPORT_TEMPLATE).render(triple_maps_details=triple_maps_details)

    return html_report
