import pytest

from ted_sws.core.model.transform import FileResource
from tests import TEST_DATA_PATH


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def rml_file():
    path = TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package" / "transformation" / "mappings" / "award_of_contract.rml.ttl"
    return FileResource(file_name="file_name", file_content=path.read_text())


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "test_package"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"
