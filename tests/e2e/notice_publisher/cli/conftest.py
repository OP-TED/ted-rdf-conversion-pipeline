from pathlib import Path

import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "validation_package"


@pytest.fixture
def fake_repository_path() -> Path:
    return TEST_DATA_PATH / "notice_validator" / "validation_repository"


@pytest.fixture
def fake_rdf_file() -> str:
    return TEST_DATA_PATH / "rdf_manifestations" / "002705-2021.ttl"