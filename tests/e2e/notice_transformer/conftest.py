from pathlib import Path

import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def rml_test_package_path() -> Path:
    return TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package"


@pytest.fixture
def rml_non_existing_test_package_path() -> Path:
    return TEST_DATA_PATH / "notice_transformer" / "test_repository" / "non_existing_test_package"


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "test_package"


@pytest.fixture
def fake_not_mapping_suite_id() -> str:
    return "test_not_package"


@pytest.fixture
def fake_failed_mapping_suite_id() -> str:
    return "test_failed_package"


@pytest.fixture
def fake_fail_repository_path() -> Path:
    return TEST_DATA_PATH / "notice_transformer" / "test_fail_packages"


@pytest.fixture
def fake_repository_path() -> Path:
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"
