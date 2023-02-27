import pytest

from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.core.model.notice import NoticeStatus, Notice
from tests import TEST_DATA_PATH


@pytest.fixture(scope="function")
def package_eligible_notice(publicly_available_notice) -> Notice:
    notice = publicly_available_notice
    notice._distilled_rdf_manifestation.object_data = (
            TEST_DATA_PATH / "notice_packager" / "templates" / "2021_S_004_003545_0.notice.rdf").read_text()
    notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    return notice
