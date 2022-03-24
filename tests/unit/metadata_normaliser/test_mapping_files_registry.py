import pandas as pd

from ted_sws.metadata_normaliser.resources.mapping_files_registry import MappingFilesRegistry


def test_mapping_file_registry():
    json_resource_files = [MappingFilesRegistry().countries, MappingFilesRegistry().notice_type,
                      MappingFilesRegistry().languages,
                      MappingFilesRegistry().legal_basis]
    for file in json_resource_files:
        assert isinstance(file, dict)
        assert "results" in file.keys()

    csv_resource_files = [MappingFilesRegistry().sf_notice_df,MappingFilesRegistry().ef_notice_df]

    for file in csv_resource_files:
        assert isinstance(file, pd.DataFrame)
        assert "eforms_subtype" in file.keys()