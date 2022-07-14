from ted_sws.notice_validator.services.xpath_coverage_runner import coverage_notice_xpath_report, CoverageRunner


def test_xpath_coverage_runner(fake_notice_F03, fake_conceptual_mappings_F03_path, fake_mapping_suite_F03_id):
    report = coverage_notice_xpath_report([fake_notice_F03], fake_mapping_suite_F03_id,
                                          fake_conceptual_mappings_F03_path)
    json_report = CoverageRunner.json_report(report)
    assert isinstance(json_report, dict)
    assert json_report["coverage"]

    html_report = CoverageRunner.html_report(report)
    assert fake_notice_F03.ted_id in html_report
