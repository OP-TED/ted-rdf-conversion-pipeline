from datetime import datetime, time, timedelta

import pytest

from ted_sws.core.model.manifestation import XMLManifestation, ValidationSummaryReport
from ted_sws.core.model.notice import Notice
from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice
from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice, \
    summary_validation_for_daily_supra_notice


def test_supra_notice_validator(fake_mongodb_client, daily_supra_notice_repository):
    day = datetime.combine(datetime.today() - timedelta(days=1), time())

    notice_ids = ["XYZ067623-2022023"]

    with pytest.raises(ValueError):
        validate_and_update_daily_supra_notice(day, fake_mongodb_client)

    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=fake_mongodb_client,
                                                    notice_fetched_date=day)
    validate_and_update_daily_supra_notice(day, fake_mongodb_client)
    result = daily_supra_notice_repository.get(reference=day)
    assert result
    assert result.notice_ids is not None
    if result.validation_report.missing_notice_ids is not None:
        assert result.validation_report.missing_notice_ids
        assert notice_ids[0] not in result.validation_report.missing_notice_ids
        assert not result.validation_report.is_valid()


def test_summary_validation_for_daily_supra_notice(fake_mongodb_client, daily_supra_notice_repository,
                                                   fake_notice_repository):
    day = datetime.combine(datetime.today() - timedelta(days=1), time())

    with pytest.raises(ValueError):
        summary_validation_for_daily_supra_notice(day, fake_mongodb_client)

    notice_id = "TEST-XYZ067623-2022023"
    notice_ids = [notice_id]

    notice = Notice(ted_id=notice_id, xml_manifestation=XMLManifestation(object_data=""))
    fake_notice_repository.add(notice)

    create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=fake_mongodb_client,
                                                    notice_fetched_date=day)

    summary_validation_for_daily_supra_notice(ted_publication_date=day, mongodb_client=fake_mongodb_client)
    result = daily_supra_notice_repository.get(reference=day)
    assert isinstance(result.validation_summary, ValidationSummaryReport)
    assert result.notice_ids == notice_ids
    assert result.validation_summary.notice_ids == []


