import pathlib
from pathlib import Path
from typing import List, Dict

from src.ted_sws.core.model.manifestation import XMLManifestation
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.core.model.transform import FileResource, MappingPackage
from src.ted_sws.core.model.validation_report import ReportNotice, ReportNoticeMetadata
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingPackageRepositoryInFileSystem


def file_resource_output_path(file_resource: FileResource, output_path: Path = '') -> Path:
    return output_path / file_resource_path(file_resource)


def file_resource_path(file_resource: FileResource) -> Path:
    return Path(*file_resource.parents)


def mapping_package_skipped_notice(notice_id: str, notice_ids: List[str]) -> bool:
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


def mapping_package_notice_path_by_group_depth(path: Path, group_depth: int = 0) -> Path:
    return MappingPackageRepositoryInFileSystem.mapping_package_notice_path_by_group_depth(path, group_depth=group_depth)


def mapping_package_notices_grouped_by_path(mapping_package: MappingPackage = None, with_content=True,
                                          file_resources: List[FileResource] = None, group_depth: int = 0,
                                          notice_ids: List[str] = None) -> Dict[Path, List[ReportNotice]]:
    grouped_notices: Dict[Path, List[ReportNotice]] = {}
    if file_resources is None:
        file_resources = mapping_package.transformation_test_data.test_data
    for data in file_resources:
        notice_id = Path(data.file_name).stem
        if mapping_package_skipped_notice(notice_id, notice_ids):
            continue
        notice = Notice(ted_id=notice_id)
        if with_content:
            notice.set_xml_manifestation(XMLManifestation(object_data=data.file_content))
        report_notice = ReportNotice(notice=notice,
                                     metadata=ReportNoticeMetadata(path=file_resource_path(data)))
        group = mapping_package_notice_path_by_group_depth(
            path=file_resource_output_path(data),
            group_depth=group_depth
        )
        grouped_notices.setdefault(group, []).append(report_notice)

    return grouped_notices


def mapping_package_files_grouped_by_path(file_resources: List[FileResource], group_depth: int = 0) \
        -> Dict[Path, List[FileResource]]:
    grouped_files: Dict[Path, List[FileResource]] = {}
    for data in file_resources:
        group = Path(*file_resource_output_path(data).parts[:(-group_depth if group_depth else None)])
        grouped_files.setdefault(group, []).append(data)

    return grouped_files


def read_flat_file_resources(path: pathlib.Path, file_resources=None, extension=None, with_content=True) -> \
        List[FileResource]:
    return MappingPackageRepositoryInFileSystem.read_flat_file_resources(
        path=path,
        file_resources=file_resources,
        extension=extension,
        with_content=with_content
    )
