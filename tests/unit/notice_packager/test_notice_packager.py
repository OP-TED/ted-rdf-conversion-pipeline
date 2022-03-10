#!/usr/bin/python3

# test_notice_packager.py
# Date:  08/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

import base64
from ted_sws.notice_packager.model.metadata import ACTION_CREATE, ACTION_UPDATE

from ted_sws.notice_packager.services.notice_packager import create_notice_package


def test_notice_packager(notice_sample_metadata):
    encoded_package_content = create_notice_package(notice_sample_metadata)
    assert encoded_package_content is not None

    raw_package_content = base64.b64decode(encoded_package_content)
    assert b'mets.xml.dmd.rdf' in raw_package_content
    assert b'mets.xml' in raw_package_content
    assert b'tmd.rdf' in raw_package_content


def test_notice_packager_with_create_action(notice_sample_metadata):
    encoded_package_content = create_notice_package(notice_sample_metadata, action=ACTION_CREATE)
    assert encoded_package_content is not None

    raw_package_content = base64.b64decode(encoded_package_content)
    assert b'mets2create.mets.xml' in raw_package_content


def test_notice_packager_with_update_action(notice_sample_metadata):
    encoded_package_content = create_notice_package(notice_sample_metadata, action=ACTION_UPDATE)
    assert encoded_package_content is not None

    raw_package_content = base64.b64decode(encoded_package_content)
    assert b'mets2update.mets.xml' in raw_package_content
