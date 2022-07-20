from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository


def test_daily_supra_notice_repository(mongodb_client, daily_supra_notice):
    daily_supra_notice_repository = DailySupraNoticeRepository(mongodb_client=mongodb_client)
    daily_supra_notice_repository.add(daily_supra_notice=daily_supra_notice)
    result_supra_notice = daily_supra_notice_repository.get(reference=daily_supra_notice.notice_publication_day)
    assert result_supra_notice
    assert len(result_supra_notice.notice_ids) == 3
    assert result_supra_notice.notice_publication_day == daily_supra_notice.notice_publication_day
    assert result_supra_notice.created_at == daily_supra_notice.created_at
    assert result_supra_notice.notice_ids == daily_supra_notice.notice_ids
    daily_supra_notice_repository.update(daily_supra_notice=daily_supra_notice)
    result_supra_notice = daily_supra_notice_repository.get(reference=daily_supra_notice.notice_publication_day)
    assert result_supra_notice
    assert len(result_supra_notice.notice_ids) == 3
    assert result_supra_notice.notice_publication_day == daily_supra_notice.notice_publication_day
    assert result_supra_notice.created_at == daily_supra_notice.created_at
    assert result_supra_notice.notice_ids == daily_supra_notice.notice_ids
    result = list(daily_supra_notice_repository.list())
    assert len(result) == 1
