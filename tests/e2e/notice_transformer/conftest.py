import pathlib

import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def rml_test_package_path() -> pathlib.Path:
    return TEST_DATA_PATH / "notice_transformer" / "test_repository" / "test_package"
