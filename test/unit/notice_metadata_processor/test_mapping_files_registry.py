import pandas as pd

from src.ted_sws.resources.mapping_files_registry import MappingFilesRegistry
from test.unit.notice_metadata_processor import load_mapping_suite_and_package


def test_mapping_file_registry(mongodb_client, load_mapping_suite_and_package):
    json_resource_files = [
        MappingFilesRegistry(mongodb_client=mongodb_client).countries,
        MappingFilesRegistry(mongodb_client=mongodb_client).notice_type,
        MappingFilesRegistry(mongodb_client=mongodb_client).languages,
        MappingFilesRegistry(mongodb_client=mongodb_client).legal_basis
    ]
    for file_content in json_resource_files:
        assert isinstance(file_content, dict)
        assert "results" in file_content.keys()

    csv_resource_files = [
        MappingFilesRegistry(mongodb_client=mongodb_client).sf_notice_df,
        MappingFilesRegistry(mongodb_client=mongodb_client).ef_notice_df
    ]

    for file_content in csv_resource_files:
        assert isinstance(file_content, pd.DataFrame)
        assert "eforms_subtype" in file_content.keys()
