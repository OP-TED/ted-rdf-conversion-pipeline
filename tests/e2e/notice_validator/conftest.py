import pytest

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from tests import TEST_DATA_PATH


@pytest.fixture
def fake_notice_id() -> str:
    return "notice"


@pytest.fixture
def fake_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository"


@pytest.fixture
def fake_mapping_suite_F03_id() -> str:
    return "test_package_F03"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def fake_conceptual_mappings_F03_path(fake_repository_path, fake_mapping_suite_F03_id) -> str:
    return str(fake_repository_path / fake_mapping_suite_F03_id / "transformation" / "conceptual_mappings.xlsx")


@pytest.fixture
def fake_notice_F03_content(fake_repository_path, fake_mapping_suite_F03_id):
    with open(fake_repository_path / fake_mapping_suite_F03_id / "test_data" / "1" / "notice.xml") as f:
        notice_content = f.read()
    return notice_content


@pytest.fixture
def fake_notice_F03(fake_notice_F03_content, fake_notice_id):
    xml_manifestation = XMLManifestation(object_data=fake_notice_F03_content)
    return Notice(ted_id=fake_notice_id, xml_manifestation=xml_manifestation)
