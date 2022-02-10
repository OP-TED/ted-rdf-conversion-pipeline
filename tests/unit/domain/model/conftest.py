#!/usr/bin/python3

# conftest.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest

from ted_sws.domain.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation
from ted_sws.domain.model.metadata import TEDMetadata, NormalisedMetadata
from ted_sws.domain.model.notice import Notice, NoticeStatus


@pytest.fixture
def fetched_notice_data():
    ted_id = "ted_id1"
    original_metadata = TEDMetadata(**{"AA": "Value here"})
    xml_manifestation = XMLManifestation(object_data="XML manifestation content")
    return ted_id, original_metadata, xml_manifestation


@pytest.fixture(scope="function")
def publicly_available_notice(fetched_notice_data):
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    notice = Notice(ted_id=ted_id, original_metadata=original_metadata,
                    xml_manifestation=xml_manifestation)
    notice._rdf_manifestation = RDFManifestation(object_data="RDF manifestation content")
    notice._mets_manifestation = METSManifestation(object_data="METS manifestation content")
    notice._normalised_metadata = NormalisedMetadata()
    notice._status = NoticeStatus.PUBLICLY_AVAILABLE
    return notice


@pytest.fixture(scope="function")
def raw_notice(fetched_notice_data):
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    notice = Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)
    return notice
