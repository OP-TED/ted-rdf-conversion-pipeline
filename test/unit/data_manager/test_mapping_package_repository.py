from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB, \
    MappingPackageRepositoryInFileSystem


def test_mapping_package_repository_mongodb(mongodb_client, fake_mapping_package,
                                          fake_mapping_package_identifier, aggregates_database_name):
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository.add(mapping_package=fake_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package_identifier)
    assert result_mapping_package
    assert result_mapping_package.identifier == fake_mapping_package.identifier
    result_mapping_package.title = "updated_title"
    mapping_package_repository.update(mapping_package=result_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package_identifier)
    assert result_mapping_package.shacl_test_suites[0].identifier == "fake_shacl_test_suite"
    assert result_mapping_package.title == "updated_title"
    result_mapping_packages = list(mapping_package_repository.list())
    assert len(result_mapping_packages) == 1
    mongodb_client.drop_database(aggregates_database_name)


def test_mapping_package_repository_mongodb_update_invalid_id(mongodb_client, fake_mapping_package,
                                                            fake_mapping_package_identifier,
                                                            aggregates_database_name):
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository.add(mapping_package=fake_mapping_package)
    result_mapping_package = mapping_package_repository.get(reference=fake_mapping_package_identifier)
    assert result_mapping_package
    assert result_mapping_package.identifier == fake_mapping_package.identifier
    result_mapping_package.identifier = "updated_id"
    result_mapping_package.title = "updated_title"
    mapping_package_repository.update(mapping_package=result_mapping_package)
    try:
        result_mapping_package = mapping_package_repository.get(reference=result_mapping_package.identifier)
    except Exception as e:
        from mapping_suite_sdk.core.adapters.repository import ModelNotFoundError
        if isinstance(e, ModelNotFoundError):
            result_mapping_package = None
        else:
            raise
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

# during the transition to MSSDK the models for writing will be different, so do a very minimal test on specific fields
def test_inter_transactions_mapping_package_repositories(mongodb_client, file_system_repository_path, fake_mapping_package,
                                                       fake_mapping_package_identifier,
                                                       aggregates_database_name):
    mapping_package_repository_mongodb = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository_file_system = MappingPackageRepositoryInFileSystem(
        repository_path=file_system_repository_path)
    mapping_package_repository_file_system.clear_repository()
    mapping_package_repository_mongodb.add(mapping_package=fake_mapping_package)
    loaded_from_mongo = mapping_package_repository_mongodb.get(reference=fake_mapping_package_identifier)
    mapping_package_repository_file_system.add(mapping_package=loaded_from_mongo)
    loaded_from_fs = mapping_package_repository_file_system.get(reference=fake_mapping_package.identifier)

    assert extract_core_fields(loaded_from_fs) == extract_core_fields(fake_mapping_package)

    mapping_package_repository_file_system.clear_repository()
    mongodb_client.drop_database(aggregates_database_name)


def extract_core_fields(mapping_package):
    """
    Extract only the stable, domain-relevant fields for comparison.
    Adjust this function as your domain model evolves.
    """
    return {
        "identifier": getattr(mapping_package, "identifier", None),
        "title": getattr(mapping_package, "title", None),
        "version": getattr(mapping_package, "version", None),
    }
