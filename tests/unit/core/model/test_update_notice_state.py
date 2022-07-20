#!/usr/bin/python3

# test_update_notice_state.py
# Date:  08/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import pytest

from ted_sws.core.model.manifestation import RDFManifestation, METSManifestation
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import NoticeStatus, UnsupportedStatusTransition


def test_updating_notice_invalid_sate(publicly_available_notice):
    with pytest.raises(ValueError):
        publicly_available_notice.update_status_to(None)


def test_setting_normalised_metadata_upstream(publicly_available_notice, normalised_metadata_dict):
    publicly_available_notice.set_normalised_metadata(publicly_available_notice.normalised_metadata)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    normalised_metadata_dict["notice_publication_number"] = "ND-UP"
    publicly_available_notice.set_normalised_metadata(NormalisedMetadata(**normalised_metadata_dict))
    assert publicly_available_notice.status is NoticeStatus.NORMALISED_METADATA
    assert publicly_available_notice.normalised_metadata is not None
    assert publicly_available_notice.rdf_manifestation is None
    assert publicly_available_notice.mets_manifestation is None


def test_setting_normalised_metadata_downstream(indexed_notice, normalised_metadata_dict):
    indexed_notice.update_status_to(NoticeStatus.INDEXED)
    indexed_notice.set_normalised_metadata(NormalisedMetadata(**normalised_metadata_dict))
    assert indexed_notice.status is NoticeStatus.NORMALISED_METADATA
    assert indexed_notice.normalised_metadata is not None
    assert indexed_notice.rdf_manifestation is None
    assert indexed_notice.mets_manifestation is None


def test_setting_rdf_manifestation_downstream(indexed_notice):
    with pytest.raises(UnsupportedStatusTransition):
        indexed_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))

    indexed_notice.update_status_to(NoticeStatus.INDEXED)
    indexed_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)
    indexed_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    indexed_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))

    assert indexed_notice.rdf_manifestation is not None
    assert indexed_notice.mets_manifestation is None


def test_setting_rdf_manifestation_upstream(publicly_available_notice):
    publicly_available_notice.set_rdf_manifestation(publicly_available_notice.rdf_manifestation)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))
    assert publicly_available_notice.status is NoticeStatus.TRANSFORMED


def test_setting_mets_manifestation_downstream(indexed_notice):
    with pytest.raises(ValueError):
        indexed_notice.set_mets_manifestation(METSManifestation(object_data="mets data"))
    indexed_notice.update_status_to(NoticeStatus.INDEXED)
    indexed_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)
    indexed_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    indexed_notice.update_status_to(NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)
    indexed_notice.set_rdf_manifestation(RDFManifestation(object_data="rdf data"))
    indexed_notice.update_status_to(NoticeStatus.DISTILLED)
    indexed_notice.update_status_to(NoticeStatus.VALIDATED)
    indexed_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    indexed_notice.set_mets_manifestation(METSManifestation(object_data="mets data"))

    assert indexed_notice.status is NoticeStatus.PACKAGED
    assert indexed_notice.rdf_manifestation is not None
    assert indexed_notice.mets_manifestation is not None


def test_setting_mets_manifestation_upstream(publicly_available_notice):
    publicly_available_notice.set_mets_manifestation(publicly_available_notice.mets_manifestation)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_mets_manifestation(METSManifestation(object_data="mets data"))
    assert publicly_available_notice.status is NoticeStatus.PACKAGED


def test_set_is_eligible_for_transformation(publicly_available_notice):
    publicly_available_notice.set_is_eligible_for_transformation(True)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_is_eligible_for_transformation(False)
    assert publicly_available_notice.status is NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION

    publicly_available_notice.set_is_eligible_for_transformation(True)
    assert publicly_available_notice.status is NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION


def test_set_is_eligible_for_packaging(publicly_available_notice):
    publicly_available_notice.set_is_eligible_for_packaging(True)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_is_eligible_for_packaging(False)
    assert publicly_available_notice.status is NoticeStatus.INELIGIBLE_FOR_PACKAGING

    publicly_available_notice.set_is_eligible_for_packaging(True)
    assert publicly_available_notice.status is NoticeStatus.ELIGIBLE_FOR_PACKAGING


def test_set_is_eligible_for_publishing(publicly_available_notice):
    publicly_available_notice.set_is_eligible_for_publishing(True)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_is_eligible_for_publishing(False)
    assert publicly_available_notice.status is NoticeStatus.INELIGIBLE_FOR_PUBLISHING

    publicly_available_notice.set_is_eligible_for_publishing(True)
    assert publicly_available_notice.status is NoticeStatus.ELIGIBLE_FOR_PUBLISHING


def test_mark_as_published(publicly_available_notice):
    publicly_available_notice.mark_as_published()
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PUBLISHING)
    publicly_available_notice.mark_as_published()
    assert publicly_available_notice.status is NoticeStatus.PUBLISHED

    publicly_available_notice.update_status_to(NoticeStatus.INELIGIBLE_FOR_PUBLISHING)
    with pytest.raises(UnsupportedStatusTransition):
        publicly_available_notice.mark_as_published()


def test_set_is_publicly_available(publicly_available_notice):
    publicly_available_notice.set_is_publicly_available(True)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.set_is_publicly_available(False)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_UNAVAILABLE

    publicly_available_notice.update_status_to(NoticeStatus.PUBLISHED)
    publicly_available_notice.set_is_publicly_available(True)
    assert publicly_available_notice.status is NoticeStatus.PUBLICLY_AVAILABLE

    publicly_available_notice.update_status_to(NoticeStatus.PACKAGED)
    with pytest.raises(UnsupportedStatusTransition):
        publicly_available_notice.set_is_publicly_available(True)

