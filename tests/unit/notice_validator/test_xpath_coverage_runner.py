from ted_sws.notice_validator.adapters.xpath_coverage_runner import CoverageRunner
from ted_sws.notice_validator.services.xpath_coverage_runner import coverage_notice_xpath_report


def test_xpath_coverage_runner(fake_notice_F03, fake_conceptual_mappings_F03_path, fake_xslt_transformer,
                               fake_mapping_suite_F03_id, mongodb_client):
    report = coverage_notice_xpath_report([fake_notice_F03], fake_mapping_suite_F03_id,
                                          fake_conceptual_mappings_F03_path, None, fake_xslt_transformer)
    json_report = CoverageRunner.json_report(report)
    assert isinstance(json_report, dict)
    assert "notice_id" in json_report
    assert "xpath_assertions" in json_report

    assert CoverageRunner.html_report(report)

    report = coverage_notice_xpath_report([fake_notice_F03], fake_mapping_suite_F03_id,
                                          fake_conceptual_mappings_F03_path, None, fake_xslt_transformer,
                                          mongodb_client)
    json_report = CoverageRunner.json_report(report)
    assert isinstance(json_report, dict)

