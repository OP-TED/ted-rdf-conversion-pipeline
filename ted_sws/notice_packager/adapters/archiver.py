#!/usr/bin/python3

# metadata_transformer.py
# Date:  02/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to archive templates, ready to be uploaded to Cellar
"""

import abc
import os
from zipfile import ZipFile
from typing import List, Union
from pathlib import Path

ARCHIVE_ZIP_FORMAT = "zip"
ARCHIVE_DEFAULT_FORMAT = ARCHIVE_ZIP_FORMAT
ARCHIVE_MODE_WRITE = 'w'
ARCHIVE_MODE_APPEND = 'a'

PATH_TYPE = Union[Path, str]
LIST_TYPE = Union[List[Path], List[str]]


class ArchiverABC(abc.ABC):
    """
    This abstract class provides methods definitions and infos for available archivers
    """

    @abc.abstractmethod
    def process_archive(self, archive_name: PATH_TYPE, files: LIST_TYPE, mode: str):
        """
        This method adds the files (based on provided archive mode) to archive
        """

    @abc.abstractmethod
    def add_folder_to_archive(self, archive: ZipFile, folder: PATH_TYPE):
        """
        This method adds folder (based on provided archive mode) to(based on provided archive mode) to archive archive
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
    def process_archive(self, archive_name: PATH_TYPE, files: LIST_TYPE, mode: str = ARCHIVE_MODE_WRITE) -> str:
        with ZipFile(archive_name, mode) as archive:
            for file in files:
                if os.path.isfile(file):
                    archive.write(file)
                else:
                    self.add_folder_to_archive(archive, file)
            archive.close()
        return archive_name

    def add_folder_to_archive(self, archive: ZipFile, folder: PATH_TYPE):
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                archive.write(path)
            elif os.path.isdir(path):
                self.add_folder_to_archive(archive, path)





