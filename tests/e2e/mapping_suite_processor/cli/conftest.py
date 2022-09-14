import mongomock
import pymongo
import pytest

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



