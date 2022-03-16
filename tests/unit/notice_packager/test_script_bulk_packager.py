#!/usr/bin/python3

# test_notice_packager.py
# Date:  14/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

import os

from ted_sws.notice_packager.entrypoints.bulk_packager import generate_packages
from tests import TEST_DATA_PATH


def test_bulk_packager():
    output_folder_path = generate_packages(1, TEST_DATA_PATH / "notice_packager" / "mets_packages" / "test_pkgs")
    assert output_folder_path is not None
    assert os.path.exists(output_folder_path)
    for f in os.listdir(output_folder_path):
        os.remove(os.path.join(output_folder_path, f))
    os.rmdir(output_folder_path)

