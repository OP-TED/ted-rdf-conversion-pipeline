from typing import List

from ted_sws.core.model.notice import Notice
from ted_sws.core.model.validation_summary_report import ValidationSummaryReportForNotices
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_validator.adapters.validation_summary_runner import ValidationSummaryRunner


def generate_validation_summary_report_notices(notices: List[Notice],
                                               with_html: bool = False) -> ValidationSummaryReportForNotices:
    validation_summary_runner = ValidationSummaryRunner()
    report = validation_summary_runner.validation_summary_for_notices(notices)
    if with_html:
        report.object_data = ValidationSummaryRunner.html_report(report)
    return report


def validation_summary_report_notice(notice: Notice, with_html: bool = False):
    validation_summary_runner = ValidationSummaryRunner()
    report = validation_summary_runner.validation_summary_for_notice(notice)
    if with_html:
        report.object_data = ValidationSummaryRunner.html_report(report)
    notice.validation_summary = report


def validation_summary_report_notice_by_id(notice_id: str, notice_repository: NoticeRepository,
                                           with_html: bool = False):
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    validation_summary_report_notice(notice=notice, with_html=with_html)
    notice_repository.update(notice=notice)
