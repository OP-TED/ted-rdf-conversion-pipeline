#!/usr/bin/python3

# conftest.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest
import json
import base64
from typing import Dict

from tests import TEST_DATA_PATH

from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from tests.conftest import read_notice


# template_metadata START


@pytest.fixture()
def template_sample_metadata() -> Dict:
    return json.load((TEST_DATA_PATH / "notice_packager" / "metadata_template.json").open())


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
def notice_metadata() -> ExtractedMetadata:
    notice_data = read_notice("045279-2018.json")
    notice_content = base64.b64decode(notice_data["content"]).decode(encoding="utf-8")
    xml_manifestation = XMLManifestation(object_data=notice_content)
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=xml_manifestation).to_metadata()

    return extracted_metadata

# notice_metadata END
