import pytest

from src.dags import TEDSWSPipelineDAGException
from src.dags.dags_utils import parse_notice_statuses_from_string, has_notices_with_failure_status
from src.ted_sws.core.model.notice import NoticeStatus


def test_validate_notice_statuses_string_variable():
    # Valid inputs with multiple statuses
    assert parse_notice_statuses_from_string('INELIGIBLE_FOR_TRANSFORMATION\nPUBLISHED') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    # Valid input with extra whitespace
    assert parse_notice_statuses_from_string('  INELIGIBLE_FOR_TRANSFORMATION  \n  PUBLISHED  ') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    # Single status
    assert parse_notice_statuses_from_string('PUBLISHED') == [NoticeStatus.PUBLISHED]

    # Valid input with empty lines (should be filtered out)
    assert parse_notice_statuses_from_string('INELIGIBLE_FOR_TRANSFORMATION\n\nPUBLISHED\n') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    # Empty string should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string('')

    # String with only whitespace should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string('   \n  \n  ')

    # Invalid status name should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string('INELIGIBLE_FOR_TRANSFORMATION\nINVALID_STATUS')

    # Non-string input should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string(['INELIGIBLE_FOR_TRANSFORMATION', 'PUBLISHED'])

    # Non-string input (number) should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string(123)


def test_has_notices_with_failure_status():
    # All notices have success statuses
    notices_status = {"notice1": NoticeStatus.PUBLISHED, "notice2": NoticeStatus.TRANSFORMED}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is False

    # Some notices have failure statuses
    notices_status = {"notice1": NoticeStatus.PUBLISHED, "notice2": NoticeStatus.RAW}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is True

    # All notices have failure statuses
    notices_status = {"notice1": NoticeStatus.RAW, "notice2": NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is True

    # Empty notices_status dictionary
    notices_status = {}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is False

    # Empty success_statuses list
    notices_status = {"notice1": NoticeStatus.PUBLISHED, "notice2": NoticeStatus.TRANSFORMED}
    success_statuses = []
    assert has_notices_with_failure_status(notices_status, success_statuses) is True
