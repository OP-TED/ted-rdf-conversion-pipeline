from datetime import datetime, time, timedelta

import pytest

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice
from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice, \
    summary_validation_for_daily_supra_notice


def test_supra_notice_validator(mongodb_client, daily_supra_notice_repository, fake_request_api):
    day = datetime.combine(datetime.today() - timedelta(days=1), time())

    with pytest.raises(ValueError):
        validate_and_update_daily_supra_notice(day, mongodb_client, fake_request_api)

    api_document_id = "067623-2022"

    notice_ids = ["1", "2", "3"]
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                                    ted_publication_date=day)
    validate_and_update_daily_supra_notice(day, mongodb_client, fake_request_api)
    result = daily_supra_notice_repository.get(reference=day)
    assert result
    assert len(result.validation_report.missing_notice_ids) > 0
    assert api_document_id in result.validation_report.missing_notice_ids
    assert not result.validation_report.is_valid()


def test_summary_validation_for_daily_supra_notice(mongodb_client, daily_supra_notice_repository, fake_notice_F03):
    day = datetime.combine(datetime.today() - timedelta(days=1), time())

    with pytest.raises(ValueError):
        summary_validation_for_daily_supra_notice(day, mongodb_client)

    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = fake_notice_F03
    notice_repository.add(notice=notice)

    notice_ids = [notice.ted_id]
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                                    ted_publication_date=day)
    summary_validation_for_daily_supra_notice(day, mongodb_client)
    result = daily_supra_notice_repository.get(reference=day)
    assert result
    assert result.validation_summary
