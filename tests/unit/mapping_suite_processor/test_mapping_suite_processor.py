from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_load_package_in_mongo_db
from tests import temporary_copy


def test_mapping_suite_processor_upload_in_mongodb(file_system_repository_path, mongodb_client,
                                                   test_package_identifier_with_version, aggregates_database_name):
    with temporary_copy(file_system_repository_path) as tmp_mapping_suite_package_path:
        mapping_suite_package_path = tmp_mapping_suite_package_path / "test_package"
        mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=mapping_suite_package_path,
                                                         mongodb_client=mongodb_client)
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(
            repository_path=tmp_mapping_suite_package_path)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_package_path.name)
        assert mapping_suite
        mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
        mapping_suite = mapping_suite_repository.get(reference=test_package_identifier_with_version)
        assert mapping_suite

    mongodb_client.drop_database(aggregates_database_name)
