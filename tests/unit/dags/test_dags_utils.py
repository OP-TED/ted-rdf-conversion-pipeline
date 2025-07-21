import pytest

from dags import TEDSWSPipelineDAGException
from dags.dags_utils import validate_notice_statuses_json_variable
from ted_sws.core.model.notice import NoticeStatus


def test_validate_notice_statuses_json_variable():
    assert validate_notice_statuses_json_variable('["INELIGIBLE_FOR_TRANSFORMATION","PUBLISHED"]') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    assert validate_notice_statuses_json_variable('[  "INELIGIBLE_FOR_TRANSFORMATION", "PUBLISHED"]') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    assert validate_notice_statuses_json_variable('[]') == []

    with pytest.raises(TEDSWSPipelineDAGException):
        validate_notice_statuses_json_variable('invalid json list')

    with pytest.raises(TEDSWSPipelineDAGException):
        validate_notice_statuses_json_variable('')

    # Only notice status name
    with pytest.raises(TEDSWSPipelineDAGException):
        validate_notice_statuses_json_variable('[  "INELIGIBLE_FOR_TRANSFORMATION", 60]')

    with pytest.raises(TEDSWSPipelineDAGException):
        validate_notice_statuses_json_variable('["INELIGIBLE_FOR_TRANSFORMATION", "INVALID_STATUS"]')
