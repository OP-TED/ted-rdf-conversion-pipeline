import pytest
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.triple_store import AllegroGraphTripleStore, FusekiAdapter
from tests import TEST_DATA_PATH


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
def fake_mapping_suite_id() -> str:
    return "test_package"


@pytest.fixture
def fuseki_triple_store():
    return FusekiAdapter(host=config.FUSEKI_ADMIN_HOST, user=config.FUSEKI_ADMIN_USER, password=config.FUSEKI_ADMIN_PASSWORD)
