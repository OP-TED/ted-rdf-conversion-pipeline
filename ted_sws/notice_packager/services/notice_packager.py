#!/usr/bin/python3

# notice_packager.py
# Date:  05/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to generate notice package.
"""

import base64
import binascii
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union

from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.notice_packager.adapters.archiver import ArchiverFactory, ARCHIVE_ZIP_FORMAT, PATH_TYPE, \
    LIST_TYPE as PATH_LIST_TYPE
from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.model.metadata import ACTION_CREATE
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer

ARCHIVE_NAME_FORMAT = "eProcurement_notice_{notice_id}.zip"
FILE_METS_XML_FORMAT = "{notice_id}-0.mets.xml.dmd.rdf"
FILE_METS_ACTION_FORMAT = "{notice_id}_mets2{action}.mets.xml"
FILE_TMD_FORMAT = "techMDID001.tmd.rdf"
FILE_RDF_FORMAT = "{notice_id}.rdf"

NOTICE_METADATA_TYPE = ExtractedMetadata
IN_DATA_TYPE = Union[NOTICE_METADATA_TYPE, Notice, str]
RDF_CONTENT_TYPE = Union[str, bytes]


def create_notice_package(in_data: IN_DATA_TYPE, rdf_content: RDF_CONTENT_TYPE = None,
                          extra_files: PATH_LIST_TYPE = None, action: str = ACTION_CREATE,
                          save_to: PATH_TYPE = None, notice_repository: NoticeRepositoryABC = None) -> str:
    """
    :param in_data: can be Notice object, ExtractedMetadata object or notice_id string
    :param rdf_content: base64 encoded bytes content of rdf file
    :param extra_files: additional files paths to be added to archive
    :param action:
    :param save_to: can be:
                    None - base64 encoded string of archive content,
                    "" - temporary archive path,
                    string (path to archive: containing archive name or just the folder) - archive path
    :param notice_repository:
    :return: base64 encoded archive or path to archive
    """

    tmp_dir = TemporaryDirectory()
    tmp_dir_path = Path(tmp_dir.name)

    notice_packager = NoticePackager(in_data, action, tmp_dir_path, notice_repository)

    notice_packager.add_template_files()
    notice_packager.add_rdf_content(rdf_content)
    notice_packager.add_extra_files(extra_files)

    return notice_packager.pack(save_to)


class NoticePackager:
    """
    This class will manage the steps/methods of notice packager creation
    """

    def __init__(self, in_data: IN_DATA_TYPE, action: str, tmp_dir_path: Path, notice_repository: NoticeRepositoryABC):
        self.notice_metadata: NOTICE_METADATA_TYPE = self.__validated_in_data(in_data, notice_repository)
        self.archiver = ArchiverFactory.get_archiver(ARCHIVE_ZIP_FORMAT)
        metadata_transformer = MetadataTransformer(self.notice_metadata)
        self.template_metadata = metadata_transformer.template_metadata(action=action)

        self.notice_id = self.template_metadata.notice.id
        self.notice_action = self.template_metadata.notice.action.type

        self.tmp_dir_path = tmp_dir_path
        self.files: PATH_LIST_TYPE = []

    def __write_template_to_file(self, file_path, template_generator, template_metadata):
        self.__write_to_file(file_path, template_generator(template_metadata))

    @classmethod
    def __write_to_file(cls, file_path, data, mode: str = 'x'):
        with open(file_path, mode) as file:
            file.write(data)
            file.close()

    @classmethod
    def __validated_in_data(cls, in_data: IN_DATA_TYPE, notice_repository: NoticeRepositoryABC) -> NOTICE_METADATA_TYPE:
        accepted_types = IN_DATA_TYPE.__args__
        if not isinstance(in_data, accepted_types):
            raise TypeError('Notice Packager accepts input data of "%s" types only' % accepted_types)

        # here, needed notice_metadata is extracted from provided in_data
        notice_metadata = None
        if isinstance(in_data, str):  # notice_id
            '''
            if we get notice_id as in_data, 
            a Notice must be assigned to in_data for next step of the validation flow
            '''
            # get Notice from DB
            notice_id = in_data
            if isinstance(notice_repository, NoticeRepositoryABC):
                in_data = notice_repository.get(reference=notice_id)
            else:
                raise TypeError('Notice Repository must be sent, if providing notice_id "%s"' % notice_id)

        if isinstance(in_data, Notice):  # Notice
            '''
            if we get Notice object as in_data, 
            notice_metadata should be extracted from it
            '''
            notice = in_data
            notice_metadata = XMLManifestationMetadataExtractor(
                xml_manifestation=notice.xml_manifestation).to_metadata()
        elif isinstance(in_data, NOTICE_METADATA_TYPE):  # ExtractedMetadata
            notice_metadata = in_data

        if not isinstance(notice_metadata, NOTICE_METADATA_TYPE):
            raise TypeError('Notice Metadata must be of "%s" type' % NOTICE_METADATA_TYPE.__name__)

        return notice_metadata

    def add_template_files(self):
        file_mets_xml_dmd_rdf = self.tmp_dir_path / FILE_METS_XML_FORMAT.format(notice_id=self.notice_id)
        self.__write_template_to_file(file_mets_xml_dmd_rdf, TemplateGenerator.mets_xml_dmd_rdf_generator,
                                      self.template_metadata)

        file_tmd_rdf = self.tmp_dir_path / FILE_TMD_FORMAT.format()
        self.__write_template_to_file(file_tmd_rdf, TemplateGenerator.tmd_rdf_generator, self.template_metadata)

        file_mets2action_mets_xml = self.tmp_dir_path / FILE_METS_ACTION_FORMAT.format(
            notice_id=self.notice_id,
            action=self.notice_action
        )
        self.__write_template_to_file(file_mets2action_mets_xml, TemplateGenerator.mets2action_mets_xml_generator,
                                      self.template_metadata)

        self.files = [
            file_mets_xml_dmd_rdf,
            file_tmd_rdf,
            file_mets2action_mets_xml
        ]

    def add_rdf_content(self, rdf_content: RDF_CONTENT_TYPE):
        if rdf_content is not None:
            if isinstance(rdf_content, str):
                rdf_content = bytes(rdf_content, 'utf-8')
            try:
                rdf_content_bytes = base64.b64decode(rdf_content, validate=True)
            except binascii.Error:
                rdf_content_bytes = rdf_content
            rdf_file_path = self.tmp_dir_path / FILE_RDF_FORMAT.format(notice_id=self.notice_id)
            self.__write_to_file(rdf_file_path, rdf_content_bytes, 'xb')
            self.files.append(rdf_file_path)

    def add_extra_files(self, extra_files: PATH_LIST_TYPE):
        if extra_files is not None:
            self.files += extra_files

    def pack(self, save_to: PATH_TYPE) -> str:
        archive_name = ARCHIVE_NAME_FORMAT.format(notice_id=self.notice_id)
        archive_path = self.tmp_dir_path / archive_name
        package_path = self.archiver.process_archive(archive_path, self.files)

        with open(package_path, "rb") as f:
            raw_archive_content = f.read()

        # TODO: clear out the return
        if save_to is None:
            archive_content = base64.b64encode(raw_archive_content)
            return str(archive_content, 'utf-8')
        else:
            if save_to:  # file or folder to save the archive to
                save_to_path = Path(save_to)
                if os.path.isdir(save_to_path):
                    save_to_path /= archive_name
                self.__write_to_file(save_to_path, raw_archive_content, 'wb')
                return str(save_to_path)
            else:  # save_to=""
                return package_path
