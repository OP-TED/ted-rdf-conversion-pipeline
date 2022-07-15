from typing import List

from pymongo import MongoClient

from ted_sws.core.model.notice import Notice
from ted_sws.notice_validator.adapters.xpath_coverage_runner import CoverageRunner, PATH_TYPE
from ted_sws.notice_validator.model.coverage_report import XPATHCoverageReport


def coverage_notice_xpath_report(notices: List[Notice], mapping_suite_id,
                                 conceptual_mappings_file_path: PATH_TYPE = None,
                                 coverage_runner: CoverageRunner = None, xslt_transformer=None,
                                 mongodb_client: MongoClient = None) -> XPATHCoverageReport:
    if not coverage_runner:
        coverage_runner = CoverageRunner(conceptual_mappings_file_path, xslt_transformer, mongodb_client)
    report: XPATHCoverageReport = coverage_runner.coverage_notice_xpath(notices, mapping_suite_id)
    return report


def xpath_coverage_json_report(report: XPATHCoverageReport) -> dict:
    return CoverageRunner.json_report(report)


def xpath_coverage_html_report(report: XPATHCoverageReport) -> str:
    return CoverageRunner.html_report(report)
