import pytest

from tests import TEST_DATA_PATH


@pytest.fixture
def path_to_test_xml_file():
    return TEST_DATA_PATH / "xslt_testing_files" / "doc.xml"


@pytest.fixture
def path_to_test_xslt_file():
    return TEST_DATA_PATH / "xslt_testing_files" / "doc.xsl"


