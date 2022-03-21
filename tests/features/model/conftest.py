#!/usr/bin/python3

# conftest.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest

from ted_sws.domain.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation, \
    RDFValidationManifestation
from ted_sws.domain.model.metadata import TEDMetadata, NormalisedMetadata
from ted_sws.domain.model.notice import Notice, NoticeStatus


@pytest.fixture
def fetched_notice_data():
    ted_id = "ted_id1"
    original_metadata = TEDMetadata(**{"AA": "Value here"})
    xml_manifestation = XMLManifestation(object_data="XML manifestation content")
    return ted_id, original_metadata, xml_manifestation


@pytest.fixture(scope="function")
def publicly_available_notice(fetched_notice_data) -> Notice:
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    validation = RDFValidationManifestation(object_data="this is a validation report")
    notice = Notice(ted_id=ted_id, original_metadata=original_metadata,
                    xml_manifestation=xml_manifestation)
    notice._rdf_manifestation = RDFManifestation(object_data="RDF manifestation content", validation=validation)
    notice._mets_manifestation = METSManifestation(object_data="METS manifestation content")
    notice._normalised_metadata = NormalisedMetadata(**{"notice_publication_number": "ND"})
    notice._status = NoticeStatus.PUBLICLY_AVAILABLE
    return notice


@pytest.fixture(scope="function")
def raw_notice(fetched_notice_data) -> Notice:
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    notice = Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)
    return notice


@pytest.fixture(scope="function")
def transformation_eligible_notice(raw_notice) -> Notice:
    raw_notice.set_normalised_metadata(normalised_metadata=NormalisedMetadata(**{"notice_publication_number": "ND-UP"}))
    raw_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    return raw_notice
