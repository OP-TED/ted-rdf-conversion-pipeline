import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def technical_mapping_f03_file_path():
    return TEST_DATA_PATH / "rml_modules" / "technical_mapping_F03.rml.ttl"


@pytest.fixture
def technical_mapping_f06_file_path():
    return TEST_DATA_PATH / "rml_modules" / "technical_mapping_F06.rml.ttl"


@pytest.fixture
def fully_connected_graph_file_path():
    return TEST_DATA_PATH / "rdf_files/fully_connected_graph.ttl"


@pytest.fixture
def not_connected_graph_file_path():
    return TEST_DATA_PATH / "rdf_files/not_connected_graph.ttl"
