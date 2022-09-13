import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "mapping_suite_processor" / "mappings"


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "package_F03_demo"


@pytest.fixture
def fake_notice_id() -> str:
    return "000163-2021"
