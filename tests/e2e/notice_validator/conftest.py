from pathlib import Path

import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def fake_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository"


@pytest.fixture
def fake_mapping_suite_F03_id() -> str:
    return "test_package_F03"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"
