import os
from pathlib import Path
from typing import List, Dict

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.validation_report import ReportNotice, ReportNoticeMetadata
from ted_sws.notice_transformer.services import DEFAULT_TRANSFORMATION_FILE_EXTENSION

from ted_sws.core.model.transform import FileResource, MappingSuite


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


def read_flat_file_resources(path: Path, file_resources=None) -> List[FileResource]:
    """
        This method reads a folder (with nested-tree structure) of resources and returns a flat list of file-type
        resources from all beyond levels.
        Used for folders that contains files with unique names, but grouped into sub-folders.
    :param path:
    :param file_resources:
    :return:
    """
    if file_resources is None:
        file_resources: List[FileResource] = []

    for root, dirs, files in os.walk(path):
        file_parents = list(Path(os.path.relpath(root, path)).parts)
        for f in files:
            file_path = Path(os.path.join(root, f))
            file_resource = FileResource(file_name=file_path.name,
                                         file_content=file_path.read_text(encoding="utf-8"),
                                         original_name=file_path.name,
                                         parents=file_parents)
            file_resources.append(file_resource)

    return file_resources


def is_rdf_file_resource(file_resource: FileResource, output_path: Path,
                         rdf_ext: str = DEFAULT_TRANSFORMATION_FILE_EXTENSION) -> bool:
    file_path = file_resource_output_path(file_resource, output_path) / Path(file_resource.file_name)
    return file_path.is_file() and file_path.suffix == rdf_ext
