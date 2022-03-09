#!/usr/bin/python3

# packager.py
# Date:  05/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.adapters.archiver import ArchiverFactory, ARCHIVE_ZIP_FORMAT
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata

from tempfile import TemporaryDirectory
import base64

ARCHIVE_NAME_FORMAT = "eProcurement_notice_{notice_id}.zip"
FILE_METS_XML_FORMAT  = "{notice_id}-0.mets.xml.dmd.rdf"
FILE_METS_ACTION_FORMAT = "{notice_id}_mets2{action}.mets.xml"
FILE_TMD_FORMAT = "techMDID001.tmd.rdf"


def create_notice_package(notice_metadata: ExtractedMetadata, save_to_file: bool = False):
    archiver = ArchiverFactory.get_archiver(ARCHIVE_ZIP_FORMAT)
    metadata_transformer = MetadataTransformer(notice_metadata)
    template_metadata = metadata_transformer.template_metadata()
    template_generator = TemplateGenerator(template_metadata)

    notice_id = template_metadata['notice']['id']
    notice_action = template_metadata['notice']['action']['type']

    tmp_dir = TemporaryDirectory()

    file_mets_xml_dmd_rdf = tmp_dir / FILE_METS_XML_FORMAT.format(notice_id=notice_id)
    with open(file_mets_xml_dmd_rdf) as file:
        file.write(template_generator.mets_xml_dmd_rdf_generator())
        file.close()

    file_tmd_rdf = tmp_dir / FILE_TMD_FORMAT.format()
    with open(file_tmd_rdf) as file:
        file.write(template_generator.tmd_rdf_generator())
        file.close()

    file_mets2action_mets_xml = tmp_dir / FILE_METS_ACTION_FORMAT.format(notice_id=notice_id, action=notice_action)
    with open(file_mets2action_mets_xml) as file:
        file.write(template_generator.mets2action_mets_xml_generator())
        file.close()

    files = [
        file_mets_xml_dmd_rdf,
        file_tmd_rdf,
        file_mets2action_mets_xml
    ]

    archive_name = tmp_dir / ARCHIVE_NAME_FORMAT.format(notice_id=notice_id)
    package_path = archiver.process_archive(archive_name, files)

    archive_content = None
    if not save_to_file:
        with open(package_path, "rb") as f:
            encoded_content = base64.b64encode(f.read())
            archive_content = encoded_content

    return package_path if save_to_file else archive_content

