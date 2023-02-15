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
import pathlib
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from ted_sws.core.model.manifestation import METSManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
from ted_sws.notice_metadata_processor.services.xml_manifestation_metadata_extractor import \
    XMLManifestationMetadataExtractor
from ted_sws.notice_packager.adapters.archiver import ArchiverFactory, ARCHIVE_ZIP_FORMAT
from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.model.metadata import ACTION_CREATE
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer
from ted_sws.notice_packager import DEFAULT_NOTICE_PACKAGE_EXTENSION

ARCHIVE_NAME_FORMAT = "{work_identifier}_{action}" + DEFAULT_NOTICE_PACKAGE_EXTENSION
FILE_METS_XML_FORMAT = "{notice_id}-0.mets.xml.dmd.rdf"
FILE_METS_ACTION_FORMAT = "{work_identifier}_{action}.mets.xml"
FILE_TMD_FORMAT = "techMDID001.tmd.rdf"
FILE_RDF_FORMAT = "{notice_id}.ttl"


def package_notice(notice: Notice) -> Notice:
    """
        This function generate METSPackage and set Notice METSManifestation.
    """

    notice_packager = NoticePackager(notice, ACTION_CREATE)
    notice_packager.add_template_files()
    notice_packager.add_rdf_content(notice.distilled_rdf_manifestation.object_data.encode("utf-8"))
    mets_manifestation_content = notice_packager.pack()
    notice.set_mets_manifestation(mets_manifestation=METSManifestation(object_data=mets_manifestation_content))
    return notice


class NoticePackager:
    """
    This class will manage the steps/methods of notice packager creation
    """

    def __init__(self, notice: Notice, action: str):
        self.tmp_dir = TemporaryDirectory()
        self.tmp_dir_path = Path(self.tmp_dir.name)
        self.notice_metadata: ExtractedMetadata = XMLManifestationMetadataExtractor(
            xml_manifestation=notice.xml_manifestation).to_metadata()
        self.archiver = ArchiverFactory.get_archiver(ARCHIVE_ZIP_FORMAT)
        metadata_transformer = MetadataTransformer(self.notice_metadata)
        self.template_metadata = metadata_transformer.template_metadata(action=action)
        self.notice_id = self.template_metadata.notice.id
        self.notice_action = self.template_metadata.notice.action.type
        self.files: List[pathlib.Path] = []

    def add_template_files(self):
        file_mets_xml_dmd_rdf = self.tmp_dir_path / FILE_METS_XML_FORMAT.format(notice_id=self.notice_id)
        file_tmd_rdf = self.tmp_dir_path / FILE_TMD_FORMAT.format()
        file_mets2action_mets_xml = self.tmp_dir_path / FILE_METS_ACTION_FORMAT.format(
            work_identifier=self.template_metadata.work.identifier,
            action=self.notice_action
        )
        encoding_type = "utf-8"
        file_mets_xml_dmd_rdf.write_text(TemplateGenerator.mets_xml_dmd_rdf_generator(self.template_metadata),
                                         encoding=encoding_type
                                         )
        file_tmd_rdf.write_text(TemplateGenerator.tmd_rdf_generator(self.template_metadata), encoding=encoding_type)
        file_mets2action_mets_xml.write_text(TemplateGenerator.mets2action_mets_xml_generator(self.template_metadata),
                                             encoding=encoding_type)
        self.files = [
            file_mets_xml_dmd_rdf,
            file_tmd_rdf,
            file_mets2action_mets_xml
        ]

    def add_rdf_content(self, rdf_content: bytes):
        """

        :param rdf_content:
        :return:
        """
        if rdf_content is not None:
            try:
                rdf_content_bytes = base64.b64decode(rdf_content, validate=True)
            except binascii.Error:
                rdf_content_bytes = rdf_content
            rdf_file_path = self.tmp_dir_path / FILE_RDF_FORMAT.format(notice_id=self.notice_id)
            rdf_file_path.write_bytes(rdf_content_bytes)
            self.files.append(rdf_file_path)

    def add_extra_files(self, extra_files: List[pathlib.Path]):
        """

        :param extra_files:
        :return:
        """
        if extra_files is not None:
            self.files += extra_files

    def get_archive_name(self) -> str:
        archive_name = ARCHIVE_NAME_FORMAT.format(
            work_identifier=self.template_metadata.work.identifier,
            action=self.template_metadata.notice.action.type
        )
        return archive_name

    def pack(self) -> str:

        archive_path = self.tmp_dir_path / self.get_archive_name()
        package_path = self.archiver.process_archive(archive_path, self.files)
        raw_archive_content = package_path.read_bytes()
        archive_content = base64.b64encode(raw_archive_content)
        return str(archive_content, 'utf-8')
