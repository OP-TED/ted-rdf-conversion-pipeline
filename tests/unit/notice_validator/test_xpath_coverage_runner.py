import os

from ted_sws.notice_validator.services.xpath_coverage_runner import coverage_notice_xpath_report


def test_xpath_coverage_runner(fake_notice_F03_content, fake_mapping_suite_F03_id, fake_conceptual_mappings_F03_path,
                               fake_xslt_transformer):
    json_report = coverage_notice_xpath_report("notice_id", fake_notice_F03_content, fake_mapping_suite_F03_id,
                                               fake_conceptual_mappings_F03_path, None, fake_xslt_transformer)
    assert isinstance(json_report, dict)
    assert "notice_id" in json_report
    assert "xpath_assertions" in json_report
    assert "xpath_desertions" in json_report
