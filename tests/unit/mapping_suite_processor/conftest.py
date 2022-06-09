import mongomock
import pymongo
import pytest

from ted_sws import config
from ted_sws.mapping_suite_processor.adapters.allegro_triple_store import AllegroGraphTripleStore
from tests import TEST_DATA_PATH


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "mapping_suite_processor_repository"


@pytest.fixture
def rml_modules_path():
    return TEST_DATA_PATH / "rml_modules"


@pytest.fixture
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    return pymongo.MongoClient('server.example.com')


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "test_package_fake"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def invalid_repository_path() -> str:
    return "non_existing_dir"


@pytest.fixture
def ttl_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "award_of_contract.rml.ttl"
    return path.read_text()


@pytest.fixture
def path_ttl_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "complementary_information.rml.ttl"
    return str(path)


@pytest.fixture
def package_folder_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository" / "test_package"


@pytest.fixture
def allegro_triple_store():
    return AllegroGraphTripleStore(host=config.ALLEGRO_HOST, user=config.AGRAPH_SUPER_USER,
                                   password=config.AGRAPH_SUPER_PASSWORD)
