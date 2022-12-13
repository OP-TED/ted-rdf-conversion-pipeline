#!/usr/bin/python3

# mapping_suite_hasher.py
# Date:  23/08/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import hashlib
import pathlib
import re
from typing import Tuple, List, Union

from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME, MS_MAPPINGS_FOLDER_NAME, MS_RESOURCES_FOLDER_NAME


class MappingSuiteHasher:
    """

    """

    def __init__(self, mapping_suite_path: Union[pathlib.Path, str]):
        self.mapping_suite_path = pathlib.Path(mapping_suite_path)

    def hash_critical_mapping_files(self) -> List[Tuple[str, str]]:
        """
            return a list of tuples <file path, file hash> for
            all files in the mappings and resources folders and
            the conceptual mapping file.
            The list of tuples is sorted by the file relative path to
                ensure a deterministic order.
        """

        def _hash_a_file(file_path: pathlib.Path) -> Tuple[str, str]:
            """
                Return a tuple of the relative file path and the file hash.
            """
            # remove new-lines to align content generated on different operating systems
            new_line_pattern = re.compile(b'\r\n|\r|\n')
            file_content = re.sub(new_line_pattern, b'', file_path.read_bytes())
            hashed_line = hashlib.sha256(file_content).hexdigest()
            relative_path = str(file_path).replace(str(self.mapping_suite_path), "")
            return relative_path, hashed_line

        files_to_hash = [
            self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME,
        ]

        mapping_files = filter(lambda item: item.is_file(),
                               (self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME /
                                MS_MAPPINGS_FOLDER_NAME).iterdir())

        mapping_resource_files = filter(lambda item: item.is_file(),
                                        (self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME /
                                         MS_RESOURCES_FOLDER_NAME).iterdir())

        files_to_hash += mapping_files
        files_to_hash += mapping_resource_files

        result = [_hash_a_file(item) for item in files_to_hash]
        result.sort(key=lambda x: x[0])
        return result

    def hash_mapping_suite(self, with_version: str = "") -> str:
        """
            Returns a hash of the mapping suite.
            Only the critical resources are hashed in the mapping suite.
            The decision which resources are "critical" is implemented
            in self.hash_critical_mapping_files() function.

            If "with_version" parameter is used, then it computed the mapping
            suite hash, including the mapping suite version.
        """
        list_of_hashes = self.hash_critical_mapping_files()
        signatures = [signature[1] for signature in list_of_hashes]
        if with_version:
            signatures += with_version
        return hashlib.sha256(str.encode(",".join(signatures))).hexdigest()
