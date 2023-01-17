import os
from pathlib import Path
from typing import List

from ted_sws.notice_transformer.services import DEFAULT_TRANSFORMATION_FILE_EXTENSION

from ted_sws.core.model.transform import FileResource


def file_resource_output_path(file_resource: FileResource, output_path: Path = '') -> Path:
    return output_path / Path(*file_resource.parents)


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
                         rdf_ext: str = DEFAULT_TRANSFORMATION_FILE_EXTENSION):
    file_path = file_resource_output_path(file_resource, output_path) / Path(file_resource.file_name)
    return file_path.is_file() and file_path.suffix == rdf_ext
