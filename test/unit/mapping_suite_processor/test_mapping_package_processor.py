from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryInFileSystem, \
    MappingPackageRepositoryMongoDB
from src.ted_sws.mapping_suite_processor.services.mapping_package_processor import \
    mapping_package_processor_load_package_in_mongo_db
from test import temporary_copy


def test_mapping_package_processor_upload_in_mongodb(file_system_repository_path, mongodb_client,
                                                   test_package_identifier_with_version, aggregates_database_name):
    with temporary_copy(file_system_repository_path) as tmp_mapping_package_path:
        mapping_package_path = tmp_mapping_package_path / "test_package"
        mapping_package_processor_load_package_in_mongo_db(mapping_package_path=mapping_package_path,
                                                         mongodb_client=mongodb_client)
        mapping_package_repository = MappingPackageRepositoryInFileSystem(
            repository_path=tmp_mapping_package_path)
        mapping_package = mapping_package_repository.get(reference=mapping_package_path.name)
        assert mapping_package
        mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
        mapping_package = mapping_package_repository.get(reference=test_package_identifier_with_version)
        assert mapping_package

    mongodb_client.drop_database(aggregates_database_name)
