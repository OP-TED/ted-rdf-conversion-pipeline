import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def resources_files_path():
    return TEST_DATA_PATH / "resources" / "mapping_files"


@pytest.fixture
def resources_shacl_files_path():
    return TEST_DATA_PATH / "resources" / "shacl_shapes"


@pytest.fixture
def resources_sparql_files_path():
    return TEST_DATA_PATH / "sparql_queries"
