from typing import List

from ted_sws.core.model.manifestation import XPATHCoverageValidationReport
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.notice_validator.adapters.xpath_coverage_runner import CoverageRunner

NOTICE_GROUPING_KEY = "grouping"


def xpath_coverage_json_report(report: XPATHCoverageValidationReport) -> dict:
    return CoverageRunner.json_report(report)


def xpath_coverage_html_report(report: XPATHCoverageValidationReport, metadata: dict = None) -> str:
    return CoverageRunner.html_report(report, metadata=metadata)


def validate_xpath_coverage_notice(notice: Notice, mapping_suite: MappingSuite) -> Notice:
    """

    :param notice:
    :param mapping_suite:
    :return:
    """
    coverage_runner = CoverageRunner(mapping_suite)
    report: XPATHCoverageValidationReport = coverage_runner.xpath_coverage_validation_report(notice=notice)
    notice.set_xml_validation(xml_validation=report)

    return notice


def validate_xpath_coverage_notices(notices: List[ReportNotice],
                                    mapping_suite: MappingSuite) -> XPATHCoverageValidationReport:
    """

    :param notices:
    :param mapping_suite:
    :return:`
    """
    coverage_runner = CoverageRunner(mapping_suite)
    report: XPATHCoverageValidationReport = coverage_runner.xpath_coverage_validation_summary_report(notices=notices)

    return report
