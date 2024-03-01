import pathlib
from typing import List

import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def notice_eligibility_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "mapping_suite_processor_repository"


@pytest.fixture
def notice_normalisation_test_data_path():
    return TEST_DATA_PATH / "notice_normalisation"


@pytest.fixture
def eforms_xml_notice_paths() -> List[pathlib.Path]:
    eforms_xml_notices_path = TEST_DATA_PATH / "eforms_samples"
    return list(eforms_xml_notices_path.glob("**/*.xml"))
