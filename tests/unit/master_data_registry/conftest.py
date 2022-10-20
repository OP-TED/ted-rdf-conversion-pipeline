import pytest

from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation
from ted_sws.core.model.notice import Notice
from tests import TEST_DATA_PATH


@pytest.fixture
def notice_with_rdf_manifestation():
    notice = Notice(ted_id="002705-2021", original_metadata={},
                    xml_manifestation=XMLManifestation(object_data="No XML data"))
    rdf_content_path = TEST_DATA_PATH / "example.ttl"
    notice._rdf_manifestation = RDFManifestation(object_data=rdf_content_path.read_text(encoding="utf-8"))
    return notice
