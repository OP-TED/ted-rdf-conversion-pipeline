from datetime import datetime, time

from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository
from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice


def test_daily_supra_notice_manager(mongodb_client, daily_supra_notice_repository):
    notice_ids = ["1", "2", "3"]
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client)
    result = daily_supra_notice_repository.get(reference=datetime.combine(datetime.today(), time()))
    assert result
