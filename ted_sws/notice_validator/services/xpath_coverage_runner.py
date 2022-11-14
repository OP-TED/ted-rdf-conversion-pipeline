from typing import List

from ted_sws.core.model.manifestation import XPATHCoverageValidationReport
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.xpath_coverage_runner import CoverageRunner, PATH_TYPE
from pymongo import MongoClient


class XPATHCoverageReportBuilder:
    """
        Given a XPATHCoverageValidationReport, generates JSON and HTML reports.
    """

    def __init__(self, xpath_coverage_report: XPATHCoverageValidationReport, with_html: bool = False):
        """

        :param xpath_coverage_report:
        :param with_html: generate HTML report
        """
        self.xpath_coverage_report = xpath_coverage_report
        self.with_html = with_html

    def generate_report(self) -> XPATHCoverageValidationReport:
        if self.with_html:
            html_report = xpath_coverage_html_report(self.xpath_coverage_report)
            self.xpath_coverage_report.object_data = html_report
        return self.xpath_coverage_report


def coverage_notice_xpath_report(notices: List[Notice], mapping_suite_id,
                                 conceptual_mappings_file_path: PATH_TYPE = None,
                                 coverage_runner: CoverageRunner = None,
                                 mongodb_client: MongoClient = None) -> XPATHCoverageValidationReport:
    if not coverage_runner:
        coverage_runner = CoverageRunner(mapping_suite_id, conceptual_mappings_file_path, mongodb_client)
    report: XPATHCoverageValidationReport = coverage_runner.coverage_notice_xpath(notices, mapping_suite_id)
    return report


def xpath_coverage_json_report(report: XPATHCoverageValidationReport) -> dict:
    return CoverageRunner.json_report(report)


def xpath_coverage_html_report(report: XPATHCoverageValidationReport) -> str:
    return CoverageRunner.html_report(report)


def validate_xpath_coverage_notice(notice: Notice, mapping_suite: MappingSuite, mongodb_client: MongoClient,
                                   with_html: bool = False):
    """

    :param notice:
    :param mapping_suite:
    :param mongodb_client:
    :param with_html: generate HTML report
    :return:
    """
    xpath_coverage_report = coverage_notice_xpath_report(notices=[notice],
                                                         mapping_suite_id=mapping_suite.get_mongodb_id(),
                                                         mongodb_client=mongodb_client)
    report_builder = XPATHCoverageReportBuilder(xpath_coverage_report=xpath_coverage_report, with_html=with_html)
    notice.set_xml_validation(xml_validation=report_builder.generate_report())


def validate_xpath_coverage_notice_by_id(notice_id: str, mapping_suite_identifier: str,
                                         mapping_suite_repository: MappingSuiteRepositoryABC,
                                         mongodb_client: MongoClient, with_html: bool = False):
    """

    :param notice_id:
    :param mapping_suite_identifier:
    :param mapping_suite_repository:
    :param mongodb_client:
    :param with_html: generate HTML report
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    mapping_suite = mapping_suite_repository.get(reference=mapping_suite_identifier)
    if mapping_suite is None:
        raise ValueError(f'Mapping suite, with {mapping_suite_identifier} id, was not found')
    validate_xpath_coverage_notice(notice=notice, mapping_suite=mapping_suite, mongodb_client=mongodb_client,
                                   with_html=with_html)
    notice_repository.update(notice=notice)
