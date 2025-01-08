#!/usr/bin/python3

# conftest.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import json
from typing import Dict

import pytest

from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.notice_metadata_processor.adapters.notice_metadata_extractor import \
    DefaultNoticeMetadataExtractor
from ted_sws.notice_metadata_processor.adapters.notice_metadata_normaliser import \
    DefaultNoticeMetadataNormaliser
from ted_sws.notice_packager.model.metadata import PackagerMetadata, NoticeMetadata, WorkMetadata, ExpressionMetadata, \
    ManifestationMetadata
from tests import TEST_DATA_PATH


# template_metadata START


@pytest.fixture
def template_sample_metadata_json() -> Dict:
    return json.load((TEST_DATA_PATH / "notice_packager" / "template_metadata.json").open())


@pytest.fixture
def sample_metadata_with_wrong_title_json() -> Dict:
    return json.load((TEST_DATA_PATH / "notice_packager" / "wrong_title" / "metadata_with_wrong_title.json").open())


@pytest.fixture
def sample_mets_xml_dmd_rdf_with_wrong_title_str() -> str:
    return (TEST_DATA_PATH / "notice_packager" / "wrong_title" / "mets_with_wrong_title.mets.xml.dmd.rdf").read_text()


@pytest.fixture
def sample_metadata_with_wrong_title(sample_metadata_with_wrong_title_json) -> PackagerMetadata:
    return PackagerMetadata(**sample_metadata_with_wrong_title_json)


@pytest.fixture
def template_sample_metadata(template_sample_metadata_json) -> PackagerMetadata:
    return PackagerMetadata(**template_sample_metadata_json)


@pytest.fixture
def template_sample_notice(template_sample_metadata) -> NoticeMetadata:
    return template_sample_metadata.notice


@pytest.fixture
def template_sample_work(template_sample_metadata) -> WorkMetadata:
    return template_sample_metadata.work


@pytest.fixture
def template_sample_expression(template_sample_metadata) -> ExpressionMetadata:
    return template_sample_metadata.expression


@pytest.fixture
def template_sample_manifestation(template_sample_metadata) -> ManifestationMetadata:
    return template_sample_metadata.manifestation


# template_metadata END


# notice_metadata START

@pytest.fixture
def notice_sample_metadata(notice_2018) -> NormalisedMetadata:
    normalised_metadata = DefaultNoticeMetadataNormaliser().normalise_metadata(
        extracted_metadata=DefaultNoticeMetadataExtractor(
            xml_manifestation=notice_2018.xml_manifestation).extract_metadata())

    return normalised_metadata


# notice_metadata END


@pytest.fixture
def rdf_content() -> str:
    return (TEST_DATA_PATH / "notice_packager" / "templates" / "2021_S_004_003545_0.notice.rdf").read_text()


@pytest.fixture
def mets_packages_path():
    return TEST_DATA_PATH / "notice_packager" / "mets_packages" / "test_pkgs"


@pytest.fixture
def rdf_files_path():
    return TEST_DATA_PATH / "notice_packager" / "mets_packages" / "rdfs"


@pytest.fixture
def non_existing_rdf_files_path():
    return TEST_DATA_PATH / "notice_packager" / "mets_packages" / "non_existing_rdfs"


@pytest.fixture
def invalid_rdf_files_path():
    return TEST_DATA_PATH / "notice_packager" / "mets_packages" / "invalid_rdfs"


@pytest.fixture
def notice_id():
    return "196390_2018"
