#!/usr/bin/python3

# notice_packager.py
# Date:  05/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to generate notice package.
"""

from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.adapters.archiver import ArchiverFactory, ARCHIVE_ZIP_FORMAT
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.notice_packager.model.metadata import ACTION_CREATE

from tempfile import TemporaryDirectory
from pathlib import Path
import base64

ARCHIVE_NAME_FORMAT = "eProcurement_notice_{notice_id}.zip"
FILE_METS_XML_FORMAT = "{notice_id}-0.mets.xml.dmd.rdf"
FILE_METS_ACTION_FORMAT = "{notice_id}_mets2{action}.mets.xml"
FILE_TMD_FORMAT = "techMDID001.tmd.rdf"
FILE_OPEN_MODE = 'x'


def create_notice_package(notice_metadata: ExtractedMetadata, action: str = ACTION_CREATE,
                          save_to_file: bool = False) -> str:
    archiver = ArchiverFactory.get_archiver(ARCHIVE_ZIP_FORMAT)
    metadata_transformer = MetadataTransformer(notice_metadata)
    template_metadata = metadata_transformer.template_metadata(action=action)

    notice_id = template_metadata['notice']['id']
    notice_action = template_metadata['notice']['action']['type']

    tmp_dir = TemporaryDirectory()
    tmp_dir_path = Path(tmp_dir.name)

    file_mets_xml_dmd_rdf = tmp_dir_path / FILE_METS_XML_FORMAT.format(notice_id=notice_id)
    with open(file_mets_xml_dmd_rdf, FILE_OPEN_MODE) as file:
        file.write(TemplateGenerator.mets_xml_dmd_rdf_generator(template_metadata))
        file.close()

    file_tmd_rdf = tmp_dir_path / FILE_TMD_FORMAT.format()
    with open(file_tmd_rdf, FILE_OPEN_MODE) as file:
        file.write(TemplateGenerator.tmd_rdf_generator(template_metadata))
        file.close()

    file_mets2action_mets_xml = tmp_dir_path / FILE_METS_ACTION_FORMAT.format(notice_id=notice_id, action=notice_action)
    with open(file_mets2action_mets_xml, FILE_OPEN_MODE) as file:
        file.write(TemplateGenerator.mets2action_mets_xml_generator(template_metadata))
        file.close()

    files = [
        file_mets_xml_dmd_rdf,
        file_tmd_rdf,
        file_mets2action_mets_xml
    ]

    archive_name = ARCHIVE_NAME_FORMAT.format(notice_id=notice_id)
    archive_path = tmp_dir_path / archive_name
    package_path = archiver.process_archive(archive_path, files)

    archive_content = None
    if not save_to_file:
        with open(package_path, "rb") as f:
            raw_archive_content = f.read()
            encoded_content = base64.b64encode(raw_archive_content)
            archive_content = encoded_content

    return package_path if save_to_file else archive_content
