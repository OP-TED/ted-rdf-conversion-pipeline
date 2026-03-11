import pytest
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB


@pytest.fixture
def load_mapping_suite_and_package(mongodb_client, mapping_suite, mapping_suite_sf, mapping_package):
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository.add(mapping_suite=mapping_suite)
    mapping_suite_repository.add(mapping_suite=mapping_suite_sf)
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository.add(mapping_package=mapping_package)
