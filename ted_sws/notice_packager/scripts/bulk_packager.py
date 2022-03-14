#!/usr/bin/python3

# notice_packager.py
# Date:  14/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides functionalities to generate bulk/multiple notice packages for test purposes.
"""

import sys
from pathlib import Path
import base64
from ted_sws.notice_packager.adapters.archiver import PATH_TYPE
from ted_sws.notice_packager.services.notice_packager import create_notice_package
from tests import TEST_DATA_PATH

DEFAULT_OUTPUT_FOLDER: Path = TEST_DATA_PATH / "notice_packager" / "mets_packages" / "pkgs"
DEFAULT_RDF_PATH: Path = TEST_DATA_PATH / "notice_packager" / "templates" / "196390_2016.rdf"


def generate_multiple_packages(files_count: int = 3000, output_folder: PATH_TYPE = DEFAULT_OUTPUT_FOLDER,
                               rdf_file: PATH_TYPE = DEFAULT_RDF_PATH):
    with open(rdf_file, "r") as f:
        rdf_content = f.read()

    encoded_rdf_content = base64.b64encode(bytes(rdf_content, 'utf-8'))

    output_folder = Path(output_folder)

    base_idx = 100000
    year = 2022


    for i in range(files_count - 1):
        output_file = output_folder / Path(str(base_idx + i) + "_" + str(year) + ".zip")
        package_path = create_notice_package(
            notice_sample_metadata,
            rdf_content=encoded_rdf_content,
            save_to=output_file
        )


count = sys.argv[1]

