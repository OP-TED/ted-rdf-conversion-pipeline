#!/usr/bin/python3

# test_notice_internal_consistency.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from ted_sws.model.metadata import OriginalMetadata
from ted_sws.model.notice import XMLManifestation, PipelineNotice


def test_notice_creation():
    # no notice can be created without XML manifestation, original metadata or status
    ted_id = "id1"
    source_url = "the best URL in the world"
    original_metadata = OriginalMetadata({"key1": "value1"})
    xml_manifestation: XMLManifestation(object_data=b"some bytes")

    notice = PipelineNotice(ted_id=ted_id, source_url=source_url, original_metadata=original_metadata,
                            xml_manifestation=xml_manifestation)

    assert notice.original_metadata == original_metadata
    assert notice.ted_id == ted_id
    assert notice.xml_manifestation == xml_manifestation
    assert notice.source_url == original_metadata
