#!/usr/bin/python3

# conftest.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest
import json
from typing import Dict

from tests import TEST_DATA_PATH

from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor


# template_metadata START


@pytest.fixture()
def template_sample_metadata() -> Dict:
    return json.load((TEST_DATA_PATH / "notice_packager" / "template_metadata.json").open())


@pytest.fixture()
def template_sample_notice(template_sample_metadata) -> Dict:
    return template_sample_metadata["notice"]


@pytest.fixture()
def template_sample_work(template_sample_metadata) -> Dict:
    return template_sample_metadata["work"]


@pytest.fixture()
def template_sample_expression(template_sample_metadata) -> Dict:
    return template_sample_metadata["expression"]


@pytest.fixture()
def template_sample_manifestation(template_sample_metadata) -> Dict:
    return template_sample_metadata["manifestation"]

# template_metadata END


# notice_metadata START

@pytest.fixture()
def notice_sample_metadata() -> ExtractedMetadata:
    notice_content = (TEST_DATA_PATH / "notice_packager" / "notice.xml").read_text(encoding="utf-8")
    xml_manifestation = XMLManifestation(object_data=notice_content)
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=xml_manifestation).to_metadata()

    return extracted_metadata

# notice_metadata END

