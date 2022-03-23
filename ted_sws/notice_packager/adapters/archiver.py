#!/usr/bin/python3

# metadata_transformer.py
# Date:  02/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to archive files
"""

import abc
import os
from pathlib import Path
from typing import List, Union
from zipfile import ZipFile, ZIP_DEFLATED

ARCHIVE_ZIP_FORMAT = "zip"
ARCHIVE_ZIP_COMPRESSION = ZIP_DEFLATED
ARCHIVE_DEFAULT_FORMAT = ARCHIVE_ZIP_FORMAT
ARCHIVE_MODE_WRITE = 'w'
ARCHIVE_MODE_APPEND = 'a'
ARCHIVE_MODE = ARCHIVE_MODE_WRITE

PATH_TYPE = Union[Path, str]
LIST_TYPE = List[PATH_TYPE]


class ArchiverABC(abc.ABC):
    """
    This abstract class provides methods definitions and infos for available archivers
    """

    @abc.abstractmethod
    def process_archive(self, archive_name: PATH_TYPE, files: LIST_TYPE, mode: str):
        """
        This method adds the files (based on provided archive mode) to archive
        """


class ArchiverFactory:
    @classmethod
    def get_archiver(cls, archive_format=ARCHIVE_DEFAULT_FORMAT):
        """Factory Method to return the needed Archiver, based on archive format"""
        archivers = {
            "zip": ZipArchiver
        }

        return archivers[archive_format]()


class ZipArchiver(ArchiverABC):
    def process_archive(self, archive_name: PATH_TYPE, files: LIST_TYPE, mode: str = ARCHIVE_MODE) -> str:
        with ZipFile(archive_name, mode=mode, compression=ARCHIVE_ZIP_COMPRESSION) as archive:
            for file in files:
                if os.path.isfile(file):
                    archive.write(file, os.path.basename(file))
            archive.close()
        return archive_name
