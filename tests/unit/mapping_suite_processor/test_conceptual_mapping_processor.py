from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB, MS_METADATA_FILE_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_load_package_in_mongo_db
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import \
    mapping_suite_processor_generate_metadata, MAPPING_SUITE_HASH
from tests import temporary_copy
import os
import json
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    mapping_suite_processor_generate_sparql_queries
import pathlib

def test_mapping_suite_processor_upload_in_mongodb(file_system_repository_path, mongodb_client):
    with temporary_copy(file_system_repository_path) as tmp_mapping_suite_package_path:
        mapping_suite_package_path = tmp_mapping_suite_package_path / "test_package"
        mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=mapping_suite_package_path,
                                                         mongodb_client=mongodb_client)
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(
            repository_path=tmp_mapping_suite_package_path)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_package_path.name)
        assert mapping_suite
        mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_package_path.name)
        assert mapping_suite

    mongodb_client.drop_database(MappingSuiteRepositoryMongoDB._database_name)


def test_mapping_suite_processor_generate_metadata(file_system_repository_path):
    with temporary_copy(file_system_repository_path) as tmp_mapping_suite_package_path:
        mapping_suite_package_path = tmp_mapping_suite_package_path / "test_package"
        metadata_file_path = (mapping_suite_package_path / MS_METADATA_FILE_NAME)
        os.remove(metadata_file_path)
        assert not metadata_file_path.is_file()
        mapping_suite_processor_generate_metadata(mapping_suite_path=mapping_suite_package_path)
        assert metadata_file_path.is_file()
        metadata = json.loads(metadata_file_path.read_text())
        assert MAPPING_SUITE_HASH in metadata

        output_metadata_file_path = mapping_suite_package_path / "other_metadata.json"
        assert not output_metadata_file_path.is_file()
        mapping_suite_processor_generate_metadata(
            mapping_suite_path=mapping_suite_package_path,
            output_metadata_file_path=output_metadata_file_path
        )
        assert output_metadata_file_path.is_file()

def test_mapping_suite_processor_generate_sparql_queries():
    conecptual_mapping_path = 'C:/Users/user/Desktop/test_sparql_generator/conceptual_mappings.xlsx'
    out_folder = 'C:/Users/user/Desktop/test_sparql_generator/sparql'
    mapping_suite_processor_generate_sparql_queries(pathlib.Path(conecptual_mapping_path), pathlib.Path(out_folder))