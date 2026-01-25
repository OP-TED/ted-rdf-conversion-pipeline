import pytest
from src.ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository
from test import TEST_DATA_PATH
from test.fakes.fake_ted_api import FakeRequestAPI


@pytest.fixture
def daily_supra_notice_repository(mongodb_client) -> DailySupraNoticeRepository:
    return DailySupraNoticeRepository(mongodb_client=mongodb_client)


@pytest.fixture
def fake_request_api():
    return FakeRequestAPI()


@pytest.fixture
def fake_notice_id() -> str:
    return "notice"


@pytest.fixture
def fake_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository"


@pytest.fixture
def fake_mapping_package_F03_id() -> str:
    return "test_package_F03"


@pytest.fixture
def fake_notice_F03_content(fake_repository_path, fake_mapping_package_F03_id):
    with open(fake_repository_path / fake_mapping_package_F03_id / "test_data" / "1" / "notice.xml") as f:
        notice_content = f.read()
    return notice_content


@pytest.fixture
def fake_notice_F03(fake_notice_F03_content, fake_notice_id):
    xml_manifestation = XMLManifestation(object_data=fake_notice_F03_content)
    notice = Notice(ted_id=fake_notice_id)
    notice.set_xml_manifestation(xml_manifestation)
    rdf_manifestation = RDFManifestation(object_data="RDF manifestation content",
                                         shacl_validations=[],
                                         sparql_validations=[]
                                         )
    notice._rdf_manifestation = rdf_manifestation
    notice._distilled_rdf_manifestation = rdf_manifestation
    return notice
