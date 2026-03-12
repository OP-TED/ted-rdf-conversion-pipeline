import mongomock
import pymongo
import pytest
from pymongo import MongoClient

from src.ted_sws import config
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.data_manager.adapters.triple_store import AllegroGraphTripleStore, FusekiAdapter

from test import TEST_DATA_PATH


@pytest.fixture
def mongodb_client():
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    return mongodb_client


@pytest.fixture
def allegro_triple_store():
    return AllegroGraphTripleStore(host=config.ALLEGRO_HOST, user=config.AGRAPH_SUPER_USER,
                                   password=config.AGRAPH_SUPER_PASSWORD)


@pytest.fixture
def ttl_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "award_of_contract.rml.ttl"
    return path.read_text()


@pytest.fixture
def path_ttl_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "complementary_information.rml.ttl"
    return str(path)


@pytest.fixture
def fake_mapping_package_id() -> str:
    return "test_package"


@pytest.fixture
def fuseki_triple_store():
    return FusekiAdapter(host=config.FUSEKI_ADMIN_HOST, user=config.FUSEKI_ADMIN_USER,
                         password=config.FUSEKI_ADMIN_PASSWORD)


@pytest.fixture
def cellar_sparql_endpoint():
    return "https://publications.europa.eu/webapi/rdf/sparql"


@pytest.fixture(scope="function")
@mongomock.patch(servers=(('server.example.com', 27017),))
def fake_mongodb_client():
    mongo_client = pymongo.MongoClient('server.example.com')
    for database_name in mongo_client.list_database_names():
        mongo_client.drop_database(database_name)
    return mongo_client


@pytest.fixture
def invalid_mapping_package_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def fake_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository"


@pytest.fixture
def path_to_file_system_repository():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def fake_notice_repository(fake_mongodb_client):
    return NoticeRepository(mongodb_client=fake_mongodb_client)


@pytest.fixture
def load_mapping_suite_and_package(mongodb_client, mapping_suite, mapping_package):
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository.add(mapping_suite=mapping_suite)
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository.add(mapping_package=mapping_package)


@pytest.fixture
def load_mapping_suite_and_package_fake(fake_mongodb_client, mapping_suite, mapping_package):
    """Load mapping suite and package into fake MongoDB (mongomock) for tests."""
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=fake_mongodb_client)
    mapping_suite_repository.add(mapping_suite=mapping_suite)
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=fake_mongodb_client)
    mapping_package_repository.add(mapping_package=mapping_package)
