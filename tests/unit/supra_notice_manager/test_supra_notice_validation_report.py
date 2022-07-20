from ted_sws.core.model.supra_notice import SupraNoticeValidationReport


def test_supra_notice_validation_report():
    validation_report = SupraNoticeValidationReport(object_data="Fake report content")
    assert validation_report.is_valid()
    validation_report.missing_notice_ids = ["1", "2"]
    assert not validation_report.is_valid()