import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def first_rml_file():
    return TEST_DATA_PATH / "rml_modules" / "technical_mapping_F03.rml.ttl"


@pytest.fixture
def second_rml_file():
    return TEST_DATA_PATH / "rml_modules" / "technical_mapping_F06.rml.ttl"
