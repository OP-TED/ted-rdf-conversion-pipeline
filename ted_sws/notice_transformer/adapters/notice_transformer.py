from typing import List

from ted_sws.core.model.notice import Notice
from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.core.model.validation_report_data import ReportNoticeData
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem


class NoticeTransformer:
    @classmethod
    def transform_report_notice(cls, report_notice: ReportNotice, group_depth: int = 0) -> ReportNoticeData:
        report_path = str(MappingSuiteRepositoryInFileSystem.mapping_suite_notice_path_by_group_depth(
            report_notice.metadata.path,
            group_depth=group_depth)) if report_notice.metadata else None
        return ReportNoticeData(
            notice_id=report_notice.notice.ted_id,
            path=report_path
        )

    @classmethod
    def transform_report_notices(cls, report_notices: List[ReportNotice]) -> List[ReportNoticeData]:
        report_datas = []
        for report_notice in report_notices:
            report_datas.append(cls.transform_report_notice(report_notice))
        return report_datas

    @classmethod
    def transform_validation_report_notices(cls, report_notices: List[ReportNotice], group_depth: int = 0) \
            -> List[ReportNoticeData]:
        report_datas = []
        for report_notice in report_notices:
            report_datas.append(cls.transform_report_notice(report_notice, group_depth=group_depth))
        return report_datas

    @classmethod
    def map_report_notices_to_notices(cls, report_notices: List[ReportNotice]) -> List[Notice]:
        notices: List[Notice] = []
        for report_notice in report_notices:
            notices.append(report_notice.notice)
        return notices
