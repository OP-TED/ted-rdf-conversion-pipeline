from pymongo import MongoClient

from ted_sws.core.model.manifestation import ValidationSummaryReport
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_validator.adapters.validation_summary_runner import ValidationSummaryRunner


class ValidationSummaryReportBuilder:
    """
        Given a XPATHCoverageValidationReport, generates JSON and HTML reports.
    """

    report: ValidationSummaryReport

    def __init__(self, report: ValidationSummaryReport):
        self.report = report

    def generate_report(self) -> ValidationSummaryReport:
        html_report = ValidationSummaryRunner.html_report(self.report)
        self.report.object_data = html_report
        return self.report


def validation_summary_report_notice(notice: Notice):
    validation_summary_report = ValidationSummaryRunner()
    notices = [notice]
    report_builder = ValidationSummaryReportBuilder(validation_summary_report.validation_summary(notices))
    notice.validation_summary = report_builder.generate_report()


def validation_summary_report_notice_by_id(notice_id: str,
                                           mongodb_client: MongoClient):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    validation_summary_report_notice(notice=notice)
    notice_repository.update(notice=notice)
