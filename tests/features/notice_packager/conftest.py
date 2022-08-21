import pytest

from ted_sws.core.model.notice import NoticeStatus, Notice


@pytest.fixture(scope="function")
def package_eligible_notice(publicly_available_notice) -> Notice:
    notice = publicly_available_notice
    notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    return notice
