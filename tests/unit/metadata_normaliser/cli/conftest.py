import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def queries_folder_path():
    return TEST_DATA_PATH / "sparql_queries"
