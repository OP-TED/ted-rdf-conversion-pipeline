import json

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.rml_to_html.services.rml_to_html import rml_files_to_html_report


def test_rml_files_to_html_report(file_system_repository_path):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=file_system_repository_path)
    triple_maps=rml_files_to_html_report(mapping_suite_identifier="test_package",mapping_suite_repository=mapping_suite_repository)

    # triple_maps_uris = [triple_map['tripleMap']["value"] for triple_map in triple_maps["results"]["bindings"]]
    # #
    # with open("triple-maps.json", "w") as file:
    #     file.write(json.dumps(triple_maps))
