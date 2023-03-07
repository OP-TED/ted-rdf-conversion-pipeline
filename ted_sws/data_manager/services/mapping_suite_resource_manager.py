import os
import pathlib
from pathlib import Path
from typing import List, Dict

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import FileResource, MappingSuite
from ted_sws.core.model.validation_report import ReportNotice, ReportNoticeMetadata
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem


def file_resource_output_path(file_resource: FileResource, output_path: Path = '') -> Path:
    return output_path / file_resource_path(file_resource)


def file_resource_path(file_resource: FileResource) -> Path:
    return Path(*file_resource.parents)


def mapping_suite_skipped_notice(notice_id: str, notice_ids: List[str]) -> bool:
    """
    This method will skip the iteration step for notice_id (where notices can be retrieved only by iterating
    through a list of values, such as files, directories) that is not present in the provided list of
    input notice_ids
    :param notice_ids:
    :param notice_id:
    :return: True if input notice_ids provided and notice_id not present and False if there is no input notice_ids
    provided or notice_id is present in the input
    """
    return notice_ids and notice_id not in notice_ids


def mapping_suite_notices_grouped_by_path(mapping_suite: MappingSuite, notice_ids: List[str] = None) -> \
        Dict[Path, List[ReportNotice]]:
    grouped_notices: Dict[Path, List[ReportNotice]] = {}
    for data in mapping_suite.transformation_test_data.test_data:
        notice_id = Path(data.file_name).stem
        if mapping_suite_skipped_notice(notice_id, notice_ids):
            continue
        notice = Notice(ted_id=notice_id)
        notice.set_xml_manifestation(XMLManifestation(object_data=data.file_content))
        report_notice = ReportNotice(notice=notice,
                                     metadata=ReportNoticeMetadata(path=file_resource_path(data)))
        group = file_resource_output_path(data)
        grouped_notices.setdefault(group, []).append(report_notice)

    return grouped_notices


def read_flat_file_resources(path: pathlib.Path, file_resources=None, extension=None) -> List[FileResource]:
    return MappingSuiteRepositoryInFileSystem.read_flat_file_resources(
        path=path,
        file_resources=file_resources,
        extension=extension
    )
