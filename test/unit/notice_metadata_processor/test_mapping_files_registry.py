import pandas as pd

from src.ted_sws.resources.mapping_files_registry import MappingFilesRegistry


def test_mapping_file_registry(mongodb_client, mapping_suite):
    json_resource_files = [
        MappingFilesRegistry(mapping_suite).countries,
        MappingFilesRegistry(mapping_suite).notice_type,
        MappingFilesRegistry(mapping_suite).languages,
        MappingFilesRegistry(mapping_suite).legal_basis
    ]
    for file_content in json_resource_files:
        assert isinstance(file_content, dict)
        assert "results" in file_content.keys()

    csv_resource_files = [
        MappingFilesRegistry(mapping_suite).sf_notice_df,
        MappingFilesRegistry(mapping_suite).ef_notice_df
    ]

    for file_content in csv_resource_files:
        assert isinstance(file_content, pd.DataFrame)
        assert "eforms_subtype" in file_content.keys()
