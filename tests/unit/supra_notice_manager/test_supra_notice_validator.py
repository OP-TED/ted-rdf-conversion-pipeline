from datetime import datetime, time

import pytest

from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice
from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice


def test_supra_notice_validator(mongodb_client, daily_supra_notice_repository, fake_request_api):
    today = datetime.combine(datetime.today(), time())

    with pytest.raises(ValueError):
        validate_and_update_daily_supra_notice(today, mongodb_client, fake_request_api)

    api_document_id = "067623-2022"

    notice_ids = ["1", "2", "3"]
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client)
    validate_and_update_daily_supra_notice(today, mongodb_client, fake_request_api)
    result = daily_supra_notice_repository.get(reference=today)
    assert result
    assert len(result.validation_report.missing_notice_ids) > 0
    assert api_document_id in result.validation_report.missing_notice_ids
    assert not result.validation_report.is_valid()

    notice_ids = [api_document_id]
    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client)
    validate_and_update_daily_supra_notice(today, mongodb_client, fake_request_api)
    result = daily_supra_notice_repository.get(reference=today)
    assert result
    assert result.validation_report.is_valid()
