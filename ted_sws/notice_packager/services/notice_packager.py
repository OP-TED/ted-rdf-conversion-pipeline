#!/usr/bin/python3

# notice_packager.py
# Date:  05/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to generate notice package.
"""

import base64
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union

from ted_sws.domain.model.notice import Notice
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.notice_packager.adapters.archiver import ArchiverFactory, ARCHIVE_ZIP_FORMAT, PATH_TYPE
from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.model.metadata import ACTION_CREATE
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer
from tests.fakes.fake_notice import FakeNotice

ARCHIVE_NAME_FORMAT = "eProcurement_notice_{notice_id}.zip"
FILE_METS_XML_FORMAT = "{notice_id}-0.mets.xml.dmd.rdf"
FILE_METS_ACTION_FORMAT = "{notice_id}_mets2{action}.mets.xml"
FILE_TMD_FORMAT = "techMDID001.tmd.rdf"
FILE_RDF_FORMAT = "{notice_id}.rdf"

NOTICE_METADATA_TYPE = ExtractedMetadata
IN_DATA_TYPE = Union[NOTICE_METADATA_TYPE, Notice, str]


def __write_template_to_file(file_path, template_generator, template_metadata):
    __write_to_file(file_path, template_generator(template_metadata))


def __write_to_file(file_path, data, mode: str = 'x'):
    with open(file_path, mode) as file:
        file.write(data)
        file.close()


def __validated_in_data(in_data: IN_DATA_TYPE) -> NOTICE_METADATA_TYPE:
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
        in_data = FakeNotice(ted_id=notice_id)

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

    return notice_metadata


def create_notice_package(in_data: IN_DATA_TYPE, rdf_content: Union[str, bytes] = None,
                          extra_files: List[PATH_TYPE] = None, action: str = ACTION_CREATE,
                          save_to: PATH_TYPE = None) -> str:
    """
    :param in_data: can be Notice object, ExtractedMetadata object or notice_id string
    :param rdf_content: base64 encoded bytes content of rdf file
    :param extra_files: additional files paths to be added to archive
    :param action:
    :param save_to:
    :return: base64 encoded archive or path to archive
    """

    notice_metadata: NOTICE_METADATA_TYPE = __validated_in_data(in_data)
    archiver = ArchiverFactory.get_archiver(ARCHIVE_ZIP_FORMAT)
    metadata_transformer = MetadataTransformer(notice_metadata)
    template_metadata = metadata_transformer.template_metadata(action=action)

    notice_id = template_metadata.notice.id
    notice_action = template_metadata.notice.action.type

    tmp_dir = TemporaryDirectory()
    tmp_dir_path = Path(tmp_dir.name)

    file_mets_xml_dmd_rdf = tmp_dir_path / FILE_METS_XML_FORMAT.format(notice_id=notice_id)
    __write_template_to_file(file_mets_xml_dmd_rdf, TemplateGenerator.mets_xml_dmd_rdf_generator, template_metadata)

    file_tmd_rdf = tmp_dir_path / FILE_TMD_FORMAT.format()
    __write_template_to_file(file_tmd_rdf, TemplateGenerator.tmd_rdf_generator, template_metadata)

    file_mets2action_mets_xml = tmp_dir_path / FILE_METS_ACTION_FORMAT.format(notice_id=notice_id, action=notice_action)
    __write_template_to_file(file_mets2action_mets_xml, TemplateGenerator.mets2action_mets_xml_generator,
                             template_metadata)

    files = [
        file_mets_xml_dmd_rdf,
        file_tmd_rdf,
        file_mets2action_mets_xml
    ]

    if rdf_content is not None:
        if isinstance(rdf_content, str):
            rdf_content = bytes(rdf_content, 'utf-8')
        rdf_file_path = tmp_dir_path / FILE_RDF_FORMAT.format(notice_id=notice_id)
        __write_to_file(rdf_file_path, base64.b64decode(rdf_content), 'xb')
        files.append(rdf_file_path)

    if extra_files is not None:
        files += extra_files

    archive_name = ARCHIVE_NAME_FORMAT.format(notice_id=notice_id)
    archive_path = tmp_dir_path / archive_name
    package_path = archiver.process_archive(archive_path, files)

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
            __write_to_file(save_to_path, raw_archive_content, 'wb')
            return str(save_to_path)
        else:  # save_to=""
            return package_path
