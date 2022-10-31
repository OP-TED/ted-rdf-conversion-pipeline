from datetime import datetime, time, timedelta

from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice
from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice


def test_supra_notice_validator(mongodb_client, daily_supra_notice_repository):
    day = datetime.combine(datetime.today() - timedelta(days=1), time())

    notice_ids = ["XYZ067623-2022023"]
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                                    notice_fetched_date=day)
    validate_and_update_daily_supra_notice(day, mongodb_client)
    result = daily_supra_notice_repository.get(reference=day)
    assert result
    assert result.notice_ids is not None
    if result.validation_report.missing_notice_ids is not None:
        assert result.validation_report.missing_notice_ids
        assert notice_ids[0] not in result.validation_report.missing_notice_ids
        assert not result.validation_report.is_valid()
