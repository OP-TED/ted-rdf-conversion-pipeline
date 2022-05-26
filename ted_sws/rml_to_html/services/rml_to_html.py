import json
from string import Template

from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner
from ted_sws.rml_to_html.resources.query_registry import QueryRegistry


def query_uri_substitution(query: str, triple_map_uri: str) -> str:
    """
    Method to replace triple map URI in the SPARQL query
    :param query:
    :param triple_map_uri:
    :return:
    """
    return Template(query).substitute(tripleMapUri=triple_map_uri)


def get_query_results(query: str, sparql_runner: SPARQLRunner) -> dict:
    return json.loads(
        sparql_runner.query(query_object=query).serialize(
            format="json").decode("utf-8"))["results"]["bindings"]


def run_queries_for_triple_map(triple_map_uri: str, query_registry: QueryRegistry, sparql_runner: SPARQLRunner) -> dict:
    return {
        "triple_map_uri":triple_map_uri,
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

def rml_files_to_html_report(mapping_suite_identifier: str,mapping_suite_repository: MappingSuiteRepositoryABC):
    mapping_suite_package = mapping_suite_repository.get(reference=mapping_suite_identifier)
    if mapping_suite_package is None:
        raise ValueError(f'Mapping suite package, with {mapping_suite_identifier} id, was not found')
    rml_files = mapping_suite_package.transformation_rule_set.rml_mapping_rules
    query_registry = QueryRegistry()

    sparql_runner = SPARQLRunner(files=rml_files)
    triple_maps = json.loads(sparql_runner.query(query_object=query_registry.TRIPLE_MAP).serialize(
                    format="json").decode("utf-8"))
    triple_maps_uris = [triple_map['tripleMap']["value"] for triple_map in triple_maps["results"]["bindings"]]
    list_of_triple_maps = {}
    for triple_map_uri in triple_maps_uris[:2]:
        triple_map_details = {}

        query = query_uri_substitution(query=query_registry.LOGICAL_SOURCE, triple_map_uri=triple_map_uri)
        logical_source = json.loads(
        sparql_runner.query(query_object=query).serialize(
            format="json").decode("utf-8"))
        triple_map_details["logical_source"] = logical_source["results"]["bindings"]
        list_of_triple_maps[triple_map_uri] = triple_map_details




    return list_of_triple_maps