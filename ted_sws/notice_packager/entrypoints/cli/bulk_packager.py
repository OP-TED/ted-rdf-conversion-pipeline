#!/usr/bin/python3

# notice_packager.py
# Date:  14/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to generate bulk/multiple notice packages for test purposes.
"""

import os
import base64
from pathlib import Path

from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.notice_packager.adapters.archiver import PATH_TYPE
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer
from ted_sws.notice_packager.services.notice_packager import create_notice_package
from tests import TEST_DATA_PATH
from tests.fakes.fake_notice import FakeNotice

DEFAULT_OUTPUT_FOLDER: Path = TEST_DATA_PATH / "notice_packager" / "mets_packages" / "pkgs"
DEFAULT_RDF_PATH: Path = TEST_DATA_PATH / "notice_packager" / "templates" / "196390_2016.rdf"
DEFAULT_FILES_COUNT: int = 3000


def generate_packages(files_count: int = DEFAULT_FILES_COUNT, output_folder: PATH_TYPE = DEFAULT_OUTPUT_FOLDER,
                      rdf_file: PATH_TYPE = DEFAULT_RDF_PATH) -> str:
    with open(rdf_file, "r") as f:
        rdf_content = f.read()

    encoded_rdf_content = base64.b64encode(bytes(rdf_content, 'utf-8'))

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    base_idx = 100000
    year = 2022

    for i in range(files_count):
        doc_id = str(base_idx + i) + "-" + str(year)
        notice_id = MetadataTransformer.normalize_value(doc_id)

        output_file = output_folder / Path(notice_id + ".zip")

        notice = FakeNotice(ted_id=notice_id)
        notice_metadata = XMLManifestationMetadataExtractor(
            xml_manifestation=notice.xml_manifestation).to_metadata()
        notice_metadata.notice_publication_number = doc_id

        create_notice_package(
            notice_metadata,
            rdf_content=encoded_rdf_content,
            save_to=output_file
        )

    return str(output_folder)
