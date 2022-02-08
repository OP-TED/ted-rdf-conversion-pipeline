#!/usr/bin/python3

# test_notice_creation.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import pytest

from ted_sws.domain.model import NoticeStatus
from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.notice import Notice


def test_manifestation_creation():
    content = "the manifestation content"
    m = XMLManifestation()
    assert str(m) == "//"
    assert m.object_data == ""

    m = XMLManifestation.new(content)
    assert m.object_data == content
    assert content in str(m)

    with pytest.raises(Exception):
        XMLManifestation.new()


def test_notice_creation(fetched_notice_data):
    # no notice can be created without XML manifestation, original metadata or status
    ted_id, source_url, original_metadata, xml_manifestation = fetched_notice_data

    notice = Notice.new(ted_id=ted_id, source_url=source_url, original_metadata=original_metadata,
                        xml_manifestation=xml_manifestation)

    assert notice.ted_id == ted_id
    assert notice.source_url == source_url
    assert notice.original_metadata == original_metadata
    assert notice.xml_manifestation == xml_manifestation
    assert notice.status == NoticeStatus.RAW

    assert all(item in ["ted_id", "source_url", "original_metadata", "xml_manifestation", "status"] for item in
               notice.to_native().keys() ) is True

    with pytest.raises(Exception):
        Notice.new()
