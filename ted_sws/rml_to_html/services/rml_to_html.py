import json

from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner
from ted_sws.rml_to_html.resources.query_registry import QueryRegistry


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


    return triple_maps