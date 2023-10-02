from ted_sws.core.model.notice import NoticeStatus
from ted_sws.core.model.supra_notice import DailyNoticesMetadata


def test_daily_notice_metadata_model(daily_notice_metadata):
    daily_notice_metadata_dict = daily_notice_metadata.model_dump()
    daily_notice_metadata_from_dict = DailyNoticesMetadata(**daily_notice_metadata_dict)
    assert daily_notice_metadata == daily_notice_metadata_from_dict
