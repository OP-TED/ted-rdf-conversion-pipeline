from deepdiff import DeepDiff

from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingPackageRepositoryMongoDB, \
    MappingPackageRepositoryInFileSystem


def test_mapping_package_repository_mongodb(mongodb_client, fake_mapping_package,
                                          fake_mapping_package_identifier_with_version, aggregates_database_name):
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository.add(mapping_package=fake_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package_identifier_with_version)
    assert result_mapping_package
    assert result_mapping_package.identifier == fake_mapping_package.identifier
    result_mapping_package.title = "updated_title"
    mapping_package_repository.update(mapping_package=result_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package_identifier_with_version)
    assert result_mapping_package.shacl_test_suites[0].identifier == "fake_shacl_test_suite"
    assert result_mapping_package.title == "updated_title"
    result_mapping_packages = list(mapping_package_repository.list())
    assert len(result_mapping_packages) == 1
    mongodb_client.drop_database(aggregates_database_name)


def test_mapping_package_repository_mongodb_update_invalid_id(mongodb_client, fake_mapping_package,
                                                            fake_mapping_package_identifier_with_version,
                                                            aggregates_database_name):
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository.add(mapping_package=fake_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package_identifier_with_version)
    assert result_mapping_package
    assert result_mapping_package.identifier == fake_mapping_package.identifier
    result_mapping_package.identifier = "updated_id"
    result_mapping_package.title = "updated_title"
    mapping_package_repository.update(mapping_package=result_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=result_mapping_package.identifier)
    assert result_mapping_package is None
    mongodb_client.drop_database(aggregates_database_name)


def test_epo_mapping_package_repository_in_file_system(file_system_repository_with_packages_path,
                                                     epo_mapping_package_name):
    assert file_system_repository_with_packages_path.exists()
    mapping_package_repository = MappingPackageRepositoryInFileSystem(
        repository_path=file_system_repository_with_packages_path)
    result_mapping_package = mapping_package_repository.get(reference=epo_mapping_package_name)
    assert result_mapping_package
    assert result_mapping_package.identifier == "package_EF16"
    assert result_mapping_package.title == "Package EF16 v1.2"
    assert result_mapping_package.mapping_type == "eforms"
    assert result_mapping_package.metadata_constraints
    constraints = result_mapping_package.metadata_constraints.constraints
    assert isinstance(constraints.start_date, list)
    assert constraints.end_date is None
    assert constraints.eforms_subtype
    assert constraints.eforms_sdk_versions


def test_mapping_package_repository_in_file_system(file_system_repository_path, fake_mapping_package):
    mapping_package_repository = MappingPackageRepositoryInFileSystem(repository_path=file_system_repository_path)
    mapping_package_repository.clear_repository()
    mapping_package_repository.add(mapping_package=fake_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package.identifier)
    assert result_mapping_package
    assert result_mapping_package.identifier == fake_mapping_package.identifier
    result_mapping_package.title = "updated_title"
    mapping_package_repository.update(mapping_package=result_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package.identifier)
    assert result_mapping_package.title == "updated_title"
    result_mapping_packages = list(mapping_package_repository.list())
    assert len(result_mapping_packages) == 1
    result_mapping_package.identifier = "new_id"
    mapping_package_repository.add(mapping_package=result_mapping_package)
    result_mapping_packages = list(mapping_package_repository.list())
    assert len(result_mapping_packages) == 2
    mapping_package_repository.clear_repository()


def test_inter_transactions_mapping_package_repositories(mongodb_client, file_system_repository_path, fake_mapping_package,
                                                       fake_mapping_package_identifier_with_version,
                                                       aggregates_database_name):
    mapping_package_repository_mongodb = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository_file_system = MappingPackageRepositoryInFileSystem(
        repository_path=file_system_repository_path)
    mapping_package_repository_file_system.clear_repository()
    mapping_package_repository_mongodb.add(mapping_package=fake_mapping_package)
    result_mapping_package = mapping_package_repository_mongodb.get(reference=fake_mapping_package_identifier_with_version)
    mapping_package_repository_file_system.add(mapping_package=result_mapping_package)
    result_mapping_package = mapping_package_repository_file_system.get(reference=fake_mapping_package.identifier)
    assert DeepDiff(result_mapping_package.model_dump(), fake_mapping_package.model_dump()) == {}
    mapping_package_repository_file_system.clear_repository()
    mongodb_client.drop_database(aggregates_database_name)
