import pytest
from pymongo import MongoClient

from src.ted_sws import config
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from src.ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from src.ted_sws.mapping_suite_processor.services.mapping_package_processor import \
    load_mapping_suite_and_packages_from_github_to_mongo_db
from src.ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice


@pytest.fixture
def mongodb_client():
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    protected_databases = ['admin', 'config', 'local']
    existing_databases = mongodb_client.list_database_names()
    databases_to_delete = list(set(existing_databases) - set(protected_databases))
    for database in databases_to_delete:
        mongodb_client.drop_database(database)
    return mongodb_client


@pytest.fixture
def notice_repository_with_indexed_notices(mongodb_client, load_mapping_suite_and_package, mapping_suite, mapping_package) -> NoticeRepository:
    """Load notices from GitHub and ensure they reference the local mapping suite/package.

    This fixture:
    1. Uses load_mapping_suite_and_package to store local suite/package in MongoDB
    2. Downloads packages from GitHub (which loads test notices into the repository)
    3. Updates all packages loaded from GitHub to reference the local mapping suite
    4. Updates all notices to reference those packages
    5. Indexes and normalizes all notices
    """
    load_mapping_suite_and_packages_from_github_to_mongo_db(
        mapping_package_name="package_F03_test",
        mongodb_client=mongodb_client,
        load_test_data=True,
        msconfig_branch="config"
    )

    # Update GitHub-loaded packages to use the local mapping suite
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    for pkg in mapping_package_repository.list():
        if pkg.id != mapping_package.id and not pkg.mapping_suite_identifier:
            # This is a GitHub-loaded package without mapping_suite_identifier
            pkg.mapping_suite_identifier = mapping_suite.id
            mapping_package_repository.update(pkg)

    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice in notice_repository.list():
        indexed_notice = index_notice(notice=notice)
        normalised_notice = normalise_notice(notice=indexed_notice, mongodb_client=mongodb_client)
        notice_repository.update(notice=normalised_notice)
    return notice_repository
