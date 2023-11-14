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
import hashlib
import pathlib
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import rdflib
from rdflib.parser import StringInputSource

from ted_sws.core.model.manifestation import METSManifestation
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.notice_packager import DEFAULT_NOTICE_PACKAGE_EXTENSION
from ted_sws.notice_packager.adapters.archiver import ZipArchiver
from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.model.metadata import METS_TYPE_CREATE
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer

ARCHIVE_NAME_FORMAT = "{work_identifier}_{action}" + DEFAULT_NOTICE_PACKAGE_EXTENSION
FILE_METS_ACTION_FORMAT = "{work_identifier}_{action}.mets.xml"
DEFAULT_RDF_FILE_FORMAT = "turtle"


# The naming convention for an TEDRDF package:
# {year}_{notice_metadata.ojs_type}_{notice_metadata.ojs_issue_number}_{notice_number}_{action}
# ex.: "2021_S_4_003544_create.zip" , where:
# year = 2021
# notice_metadata.ojs_type = S
# notice_metadata.ojs_issue_number = 4
# notice_number = 003544
# action = create


def package_notice(notice: Notice, action: str = METS_TYPE_CREATE) -> Notice:
    """
        This function generate METSPackage and set Notice METSManifestation.
    """

    notice_packager = NoticePackager(notice, action)
    notice_packager.add_template_files()
    notice_packager.add_rdf_content()
    package_name = notice_packager.get_archive_name()
    mets_manifestation_content = notice_packager.pack(package_name=package_name)
    notice.set_mets_manifestation(
        mets_manifestation=METSManifestation(
            object_data=mets_manifestation_content,
            type=action,
            package_name=package_name
        )
    )
    return notice


class NoticePackager:
    """
    This class will manage the steps/methods of notice packager creation
    """

    def __init__(self, notice: Notice, action: str):
        self.tmp_dir = TemporaryDirectory()
        self.tmp_dir_path = Path(self.tmp_dir.name)
        notice_metadata: NormalisedMetadata = notice.normalised_metadata
        metadata_transformer = MetadataTransformer(notice_metadata)
        self.template_metadata = metadata_transformer.template_metadata(action=action)
        self.notice_id = self.template_metadata.notice.id
        self.action = self.template_metadata.mets.type
        self.files: List[pathlib.Path] = []

        self.rdf_content = self.get_rdf_content_from_notice(notice)
        if self.rdf_content is not None:
            rdf_hash = hashlib.sha256()
            rdf_hash.update(self.rdf_content)
            self.template_metadata.mets.notice_file_checksum = rdf_hash.hexdigest()

    def add_template_files(self):
        file_mets_xml_dmd_rdf = self.tmp_dir_path / self.template_metadata.mets.dmd_href
        file_tmd_rdf = self.tmp_dir_path / self.template_metadata.mets.tmd_href
        file_mets2action_mets_xml = self.tmp_dir_path / FILE_METS_ACTION_FORMAT.format(
            work_identifier=self.template_metadata.work.identifier,
            action=self.action
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

    @staticmethod
    def get_rdf_content_from_notice(notice: Notice) -> bytes:
        rdf_content_bytes = None
        encoding = "utf-8"
        rdf_content = notice.distilled_rdf_manifestation.object_data.encode(encoding)
        if rdf_content is not None:
            try:
                rdf_content_bytes = base64.b64decode(rdf_content, validate=True)
            except binascii.Error:
                rdf_content_bytes = rdf_content

            # transform n3 (turtle) to RDF/XML
            g = rdflib.Graph()
            g.parse(StringInputSource(rdf_content_bytes, encoding=encoding), format=DEFAULT_RDF_FILE_FORMAT)
            rdf_content_bytes = g.serialize(format='pretty-xml', encoding=encoding)

        return rdf_content_bytes

    def add_rdf_content(self):
        """
        :return:
        """
        if self.rdf_content is not None:
            rdf_file_path = self.tmp_dir_path / self.template_metadata.mets.notice_file_href
            rdf_file_path.write_bytes(self.rdf_content)
            self.files.append(rdf_file_path)

    def get_archive_name(self) -> str:
        archive_name = ARCHIVE_NAME_FORMAT.format(
            work_identifier=self.template_metadata.work.identifier,
            action=self.template_metadata.mets.type
        )
        return archive_name

    def pack(self, package_name: str = None) -> str:
        package_name = package_name or self.get_archive_name()
        archiver = ZipArchiver()
        archive_path = self.tmp_dir_path / package_name
        package_path = archiver.process_archive(archive_path, self.files)
        raw_archive_content = package_path.read_bytes()
        archive_content = base64.b64encode(raw_archive_content)
        return str(archive_content, 'utf-8')
