from ted_sws.core.model.manifestation import ValidationSummaryReport
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_validator.adapters.validation_summary_runner import ValidationSummaryRunner
from typing import List


class ValidationSummaryReportBuilder:
    """
        Given a XPATHCoverageValidationReport, generates JSON and HTML reports.
    """

    report: ValidationSummaryReport

    def __init__(self, report: ValidationSummaryReport, with_html: bool = False):
        self.report = report
        self.with_html = with_html

    def generate_report(self) -> ValidationSummaryReport:
        if self.with_html:
            html_report = ValidationSummaryRunner.html_report(self.report)
            self.report.object_data = html_report
        return self.report


def generate_validation_summary_report_notices(notices: List[Notice],
                                               with_html: bool = False) -> ValidationSummaryReport:
    validation_summary_report = ValidationSummaryRunner()
    report_builder = ValidationSummaryReportBuilder(validation_summary_report.validation_summary(notices),
                                                    with_html=with_html)
    return report_builder.generate_report()


def validation_summary_report_notice(notice: Notice, with_html: bool = False):
    notice.validation_summary = generate_validation_summary_report_notices([notice], with_html=with_html)


def validation_summary_report_notice_by_id(notice_id: str, notice_repository: NoticeRepository,
                                           with_html: bool = False):
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    validation_summary_report_notice(notice=notice, with_html=with_html)
    notice_repository.update(notice=notice)
