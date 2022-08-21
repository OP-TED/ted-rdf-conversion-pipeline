import pytest

from ted_sws.notice_validator.services.validation_summary_runner import validation_summary_report_notice_by_id
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository


def test_validation_summary_runner(fake_validation_notice, mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=fake_validation_notice)
    with pytest.raises(ValueError):
        validation_summary_report_notice_by_id(notice_id="invalid_id", notice_repository=notice_repository)
    with pytest.raises(ValueError):
        validation_summary_report_notice_by_id(notice_id="", notice_repository=notice_repository)
    validation_summary_report_notice_by_id(notice_id=fake_validation_notice.ted_id, notice_repository=notice_repository)
    notice = notice_repository.get(reference=fake_validation_notice.ted_id)
    assert notice.validation_summary
    assert notice.validation_summary.object_data
    assert notice.validation_summary.xml_manifestation
    assert notice.validation_summary.rdf_manifestation
    assert notice.validation_summary.distilled_rdf_manifestation