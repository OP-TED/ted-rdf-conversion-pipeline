from typing import List

from ted_sws.core.model.notice import Notice
from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.core.model.validation_report_data import ReportNoticeData

NOTICE_IDS_FIELD = "notice_ids"


def transform_report_notice(report_notice: ReportNotice) -> ReportNoticeData:
    return ReportNoticeData(notice_id=report_notice.notice.ted_id, path=str(report_notice.metadata.path))


def transform_report_notices(report_notices: List[ReportNotice]) -> List[ReportNoticeData]:
    report_datas = []
    for report_notice in report_notices:
        report_datas.append(transform_report_notice(report_notice))
    return report_datas


def transform_validation_report_notices(report_notices: List[Notice]) -> List[ReportNoticeData]:
    report_datas = []
    for report_notice in report_notices:
        report_datas.append(ReportNoticeData(notice_id=report_notice.ted_id))
    return report_datas
