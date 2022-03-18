from ted_sws.metadata_normaliser.resources.mapping_files_registry import MappingFilesRegistry


def test_mapping_file_registry():
    resource_files = [MappingFilesRegistry().countries, MappingFilesRegistry().notice_type,
                      MappingFilesRegistry().languages,
                      MappingFilesRegistry().legal_basis]
    for file in resource_files:
        assert isinstance(file, dict)
        assert "results" in file.keys()
