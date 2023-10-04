from ted_sws.core.model.notice import NoticeStatus
from ted_sws.core.model.supra_notice import DailyNoticesMetadata


def test_daily_notice_metadata_model(daily_notice_metadata: DailyNoticesMetadata):
    daily_notice_metadata_dict = daily_notice_metadata.model_dump()
    daily_notice_metadata_from_dict = DailyNoticesMetadata(**daily_notice_metadata_dict)
    assert daily_notice_metadata == daily_notice_metadata_from_dict

    assert daily_notice_metadata.fetched_notices_coverage == 0
    assert daily_notice_metadata.ted_api_notice_count == 0
    assert daily_notice_metadata.fetched_notices_count == 0

    daily_notice_metadata.ted_api_notice_ids = ["1", "2", "3"]
    daily_notice_metadata.fetched_notice_ids = ["1", "2"]

    assert daily_notice_metadata.fetched_notices_coverage == 0.6666666666666666
    assert daily_notice_metadata.ted_api_notice_count == 3
    assert daily_notice_metadata.fetched_notices_count == 2

    daily_notice_metadata.notice_statuses = {str(NoticeStatus.PUBLISHED): 1, str(NoticeStatus.RAW): 2}
    assert daily_notice_metadata.notice_statuses_coverage == {"PUBLISHED_coverage": 0.3333333333333333,
                                                              "RAW_coverage": 0.6666666666666666}
