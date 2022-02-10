import pytest

from ted_sws.domain.model.notice import Notice, NoticeStatus


def test_status_transition(fetched_notice_data):
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    notice = Notice(ted_id=ted_id, original_metadata=original_metadata,
                    xml_manifestation=xml_manifestation)
    # Notice can't go from RAW state to INELIGIBLE_FOR_TRANSFORMATION state
    with pytest.raises(Exception) as e:
        notice.update_status_to(value=NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION)
    assert str(
        e.value) == "Invalid transition from state NoticeStatus.RAW to state NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION"
    # Notice can go from RAW state to NORMALISED_METADATA state

    notice.update_status_to(value=NoticeStatus.NORMALISED_METADATA)

    assert notice.status
    assert isinstance(notice.status, NoticeStatus)
    assert notice.status.name == "NORMALISED_METADATA"
