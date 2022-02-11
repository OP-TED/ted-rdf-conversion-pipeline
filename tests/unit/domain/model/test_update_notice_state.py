#!/usr/bin/python3

# test_update_notice_state.py
# Date:  08/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import pytest

from ted_sws.domain.model.manifestation import RDFManifestation, METSManifestation
from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import NoticeStatus, UnsupportedStatusTransition


def test_setting_normalised_metadata_upstream(publicly_available_notice):
    publicly_available_notice.set_normalised_metadata(publicly_available_notice.normalised_metadata)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_normalised_metadata(NormalisedMetadata())
    assert publicly_available_notice.status is NoticeStatus.NORMALISED_METADATA
    assert publicly_available_notice.normalised_metadata is not None
    assert publicly_available_notice.rdf_manifestation is None
    assert publicly_available_notice.mets_manifestation is None


def test_setting_normalised_metadata_downstream(raw_notice):
    raw_notice.set_normalised_metadata(NormalisedMetadata())
    assert raw_notice.status is NoticeStatus.NORMALISED_METADATA
    assert raw_notice.normalised_metadata is not None
    assert raw_notice.rdf_manifestation is None
    assert raw_notice.mets_manifestation is None


def test_setting_rdf_manifestation_downstream(raw_notice):
    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))

    raw_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)
    raw_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    raw_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))

    assert raw_notice.rdf_manifestation is not None
    assert raw_notice.mets_manifestation is None


def test_setting_rdf_manifestation_upwnstream(publicly_available_notice):
    publicly_available_notice.set_rdf_manifestation(publicly_available_notice.rdf_manifestation)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE


    publicly_available_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))
    assert publicly_available_notice.status is NoticeStatus.TRANSFORMED


def test_setting_mets_manifestation_downstream(raw_notice):
    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.set_mets_manifestation(METSManifestation(object_data="mets data"))

    raw_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)
    raw_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    raw_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))
    raw_notice.update_status_to(NoticeStatus.VALIDATED)
    raw_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    raw_notice.set_mets_manifestation(METSManifestation(object_data="mets data"))

    assert raw_notice.status is NoticeStatus.PACKAGED
    assert raw_notice.rdf_manifestation is not None
    assert raw_notice.mets_manifestation is not None


def test_setting_mets_manifestation_upstream(publicly_available_notice):
    publicly_available_notice.set_mets_manifestation(publicly_available_notice.mets_manifestation)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_mets_manifestation(METSManifestation(object_data="mets data"))
    assert publicly_available_notice.status is NoticeStatus.PACKAGED
