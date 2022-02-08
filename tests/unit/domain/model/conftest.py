#!/usr/bin/python3

# conftest.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest

from ted_sws.domain.model.manifestation import XMLManifestation


@pytest.fixture
def fetched_notice_data():
    ted_id = "ted_id1"
    source_url = "http://the.best.URL.com/in.the.world"
    original_metadata = {"key1": "value1"}
    xml_manifestation = XMLManifestation.new("the manifestation content")

    return ted_id, source_url, original_metadata, xml_manifestation
