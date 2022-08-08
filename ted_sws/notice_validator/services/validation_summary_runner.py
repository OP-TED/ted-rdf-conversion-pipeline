from pymongo import MongoClient

from ted_sws.core.model.manifestation import ValidationSummaryReport
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_validator.adapters.xpath_coverage_runner import CoverageRunner


class ValidationSummaryReportBuilder:
    """
        Given a XPATHCoverageValidationReport, generates JSON and HTML reports.
    """

    def __init__(self, validation_summary_report: ValidationSummaryReport):
        self.validation_summary_report = validation_summary_report

    def generate_report(self) -> ValidationSummaryReport:
        html_report = CoverageRunner.html_report(self.validation_summary_report)
        self.validation_summary_report.object_data = html_report
        return self.validation_summary_report


def validation_summary_report_notice(notice: Notice, mongodb_client: MongoClient):
    validation_summary_report = coverage_notice_xpath_report(notices=[notice],
                                                         mapping_suite_id=mapping_suite.identifier,
                                                         mongodb_client=mongodb_client)
    report_builder = XPATHCoverageReportBuilder(xpath_coverage_report=xpath_coverage_report)
    notice.set_xml_validation(xml_validation=report_builder.generate_report())


def validation_summary_report_notice_by_id(notice_id: str,
                                           mongodb_client: MongoClient):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    validation_summary_report_notice(notice=notice, mongodb_client=mongodb_client)
    notice_repository.update(notice=notice)
