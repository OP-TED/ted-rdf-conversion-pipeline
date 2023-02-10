from datetime import date

from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice


def test_daily_supra_notice_manager(mongodb_client, daily_supra_notice_repository):
    notice_ids = ["1", "2", "3"]
    ted_publication_date = date(2020, 1, 1)
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                                    ted_publication_date=ted_publication_date)
    for result in daily_supra_notice_repository.list():
        assert result
    result = daily_supra_notice_repository.get(reference=ted_publication_date)
    assert result
    assert result.ted_publication_date == ted_publication_date
    notice_ids.append("4")
    result.notice_ids = notice_ids
    daily_supra_notice_repository.update(daily_supra_notice=result)
    result = daily_supra_notice_repository.get(reference=ted_publication_date)
    assert result.notice_ids == notice_ids
