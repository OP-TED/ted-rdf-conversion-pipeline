#!/usr/bin/python3

# test_notice_packager.py
# Date:  08/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

import base64
import os

import pytest

from ted_sws.notice_packager.model.metadata import ACTION_CREATE, ACTION_UPDATE
from ted_sws.notice_packager.services.notice_packager import create_notice_package
from tests import TEST_DATA_PATH


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


def test_notice_packager_with_wrong_input_data_type(notice_sample_metadata):
    input_data = 123  # wrong input_data type
    with pytest.raises(TypeError):
        create_notice_package(input_data)


def test_notice_packager_with_notice(notice_2018):
    encoded_package_content = create_notice_package(notice_2018)
    assert encoded_package_content is not None


def test_notice_packager_with_notice_id(notice_2018, notice_repository):
    notice_id = 'fake-notice-id'

    notice_repository.add(notice_2018)
    encoded_package_content = create_notice_package(in_data=notice_2018.ted_id, notice_repository=notice_repository)
    assert encoded_package_content is not None

    with pytest.raises(TypeError):
        create_notice_package(in_data=notice_id, notice_repository=None)

    with pytest.raises(TypeError):
        notice_id = 'fake-wrong-notice-id'
        create_notice_package(in_data=notice_id, notice_repository=notice_repository)


def test_notice_packager_with_extra_files(notice_2018):
    encoded_package_content = create_notice_package(
        notice_2018,
        extra_files=[
            TEST_DATA_PATH / "notice_packager" / "notice.xml"
        ]
    )
    assert encoded_package_content is not None


def test_notice_packager_with_non_existent_files(notice_2018):
    encoded_package_content = create_notice_package(
        notice_2018,
        extra_files=[
            TEST_DATA_PATH / "notice_packager" / "non_existent_notice_file.xml"
        ]
    )
    assert encoded_package_content is not None


def test_notice_packager_with_rdf_content(notice_2018, rdf_content):
    encoded_rdf_content = base64.b64encode(bytes(rdf_content, 'utf-8'))
    encoded_package_content = create_notice_package(
        notice_2018,
        rdf_content=encoded_rdf_content
    )
    assert encoded_package_content is not None

    encoded_package_content = create_notice_package(
        notice_2018,
        rdf_content=str(encoded_rdf_content, 'utf-8')
    )
    assert encoded_package_content is not None

    encoded_package_content = create_notice_package(
        notice_2018,
        rdf_content=rdf_content.encode("utf-8")
    )
    assert encoded_package_content is not None


def test_notice_packager_with_save_to(notice_sample_metadata, rdf_content):
    package_path = create_notice_package(
        notice_sample_metadata,
        save_to=TEST_DATA_PATH / "notice_packager" / "packages" / "fake-archive.zip"
    )
    assert os.path.exists(package_path)
    os.remove(package_path)

    package_path = create_notice_package(
        notice_sample_metadata,
        save_to=TEST_DATA_PATH / "notice_packager" / "packages"
    )
    assert os.path.exists(package_path)
    os.remove(package_path)

    encoded_rdf_content = base64.b64encode(bytes(rdf_content, 'utf-8'))
    package_path = create_notice_package(
        notice_sample_metadata,
        rdf_content=encoded_rdf_content,
        save_to=TEST_DATA_PATH / "notice_packager" / "packages" / "fake-rdf.zip"
    )
    assert os.path.exists(package_path)
    os.remove(package_path)

    package_path = create_notice_package(
        notice_sample_metadata,
        save_to=""
    )
    assert package_path is not None
