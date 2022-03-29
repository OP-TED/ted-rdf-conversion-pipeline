#!/usr/bin/python3

# test_notice_creation.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from pprint import pprint

from deepdiff import DeepDiff
import pytest
from pydantic import ValidationError

from ted_sws.core.model.manifestation import XMLManifestation, Manifestation, ManifestationMimeType
from ted_sws.core.model.notice import Notice, NoticeStatus


def test_manifestation_invalid_creation():
    with pytest.raises(ValidationError):
        m = XMLManifestation()


def test_manifestation_creation():
    content = "the manifestation content"
    manifestation = XMLManifestation(object_data=content)

    assert manifestation.object_data == content
    assert content in str(manifestation)


def test_notice_creation(fetched_notice_data):
    # no notice can be created without XML manifestation, original metadata or status
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    notice = Notice(ted_id=ted_id, original_metadata=original_metadata,
                    xml_manifestation=xml_manifestation)

    assert notice.ted_id == ted_id
    assert notice.original_metadata == original_metadata
    assert notice.xml_manifestation
    assert notice.status == NoticeStatus.RAW

    assert notice.ted_id in str(notice)
    assert notice.status.name in str(notice)


def test_notice_invalid_creation():
    with pytest.raises(Exception):
        notice = Notice()


def test_notice_status_validation(raw_notice):
    raw_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)
    assert "status" in raw_notice.dict().keys()
    assert "_status" not in raw_notice.dict().keys()


def test_notice_status_comparison():
    with pytest.raises(ValueError):
        assert NoticeStatus.RAW < ManifestationMimeType.TURTLE

    with pytest.raises(ValueError):
        assert NoticeStatus.RAW > ManifestationMimeType.TURTLE


