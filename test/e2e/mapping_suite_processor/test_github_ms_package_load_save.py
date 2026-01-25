from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from src.ted_sws.mapping_suite_processor.services.mapping_package_processor import \
    load_mapping_suite_and_packages_from_github_to_mongo_db

MAPPING_PACKAGE_NAME = "package_F03_test"
MAPPING_PACKAGE_METADATA_IDENTIFIER = "package_F03"
MAPPING_PACKAGE_METADATA_VERSION = "6.8.1"
MAPPING_PACKAGE_ID = f"{MAPPING_PACKAGE_METADATA_IDENTIFIER}_v{MAPPING_PACKAGE_METADATA_VERSION}"


def test_load_mapping_suite_and_packages_from_github_to_mongo_db(fake_mongodb_client):
    load_mapping_suite_and_packages_from_github_to_mongo_db(
        mapping_package_name=MAPPING_PACKAGE_NAME,
        mongodb_client=fake_mongodb_client,
        load_test_data=True
    )
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=fake_mongodb_client)
    mapping_package = mapping_package_repository.get(reference=MAPPING_PACKAGE_ID)
    assert mapping_package
