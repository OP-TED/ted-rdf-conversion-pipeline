#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """

import pytest

from ted_sws.domain.model.notice import Notice, NoticeStatus, UnsupportedStatusTransition


def test_illegal_status_transitions(raw_notice):
    """
        Test a few illegal downstream transitions.
    :param raw_notice:
    :return:
    """

    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.update_status_to(NoticeStatus.TRANSFORMED)

    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.update_status_to(NoticeStatus.PACKAGED)

    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.update_status_to(NoticeStatus.VALIDATED)

    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.update_status_to(NoticeStatus.PUBLISHED)

    with pytest.raises(UnsupportedStatusTransition):
        raw_notice.update_status_to(NoticeStatus.PUBLICLY_AVAILABLE)


def test_notice_status_upstream_transition(raw_notice):
    """
        Downstream transitions constraints checked.

    :param raw_notice:
    :return:
    """
    raw_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)
    raw_notice.update_status_to(NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION)
    raw_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    raw_notice.update_status_to(NoticeStatus.TRANSFORMED)
    raw_notice.update_status_to(NoticeStatus.VALIDATED)
    raw_notice.update_status_to(NoticeStatus.INELIGIBLE_FOR_PACKAGING)
    raw_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    raw_notice.update_status_to(NoticeStatus.PACKAGED)
    raw_notice.update_status_to(NoticeStatus.FAULTY_PACKAGE)
    raw_notice.update_status_to(NoticeStatus.CORRECT_PACKAGE)
    raw_notice.update_status_to(NoticeStatus.PUBLISHED)
    raw_notice.update_status_to(NoticeStatus.PUBLICLY_UNAVAILABLE)
    raw_notice.update_status_to(NoticeStatus.PUBLICLY_AVAILABLE)


def test_notice_status_transition_below_packaged(publicly_available_notice):
    """
        Notice status transition below PACKAGING should remove the METS manifestation
    :param publicly_available_notice:
    :return:
    """
    publicly_available_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    assert publicly_available_notice.mets_manifestation is None
    assert publicly_available_notice.rdf_manifestation is not None
    assert publicly_available_notice.normalised_metadata is not None
    assert publicly_available_notice.xml_manifestation is not None
    assert publicly_available_notice.original_metadata is not None


def test_notice_status_transition_below_transformed(publicly_available_notice):
    """
        Notice status transition below TRANSFORMED should remove the RDF and METS manifestations.
    :param publicly_available_notice:
    :return:
    """
    publicly_available_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    assert publicly_available_notice.mets_manifestation is None
    assert publicly_available_notice.rdf_manifestation is None
    assert publicly_available_notice.normalised_metadata is not None
    assert publicly_available_notice.xml_manifestation is not None
    assert publicly_available_notice.original_metadata is not None


def test_notice_status_transition_below_normalised_metadata(publicly_available_notice):
    """
    Notice status transition below TRANSFORMED should remove the normalised metadata and the RDF and METS
    manifestations. :param publicly_available_notice: :return:
    """
    publicly_available_notice.update_status_to(NoticeStatus.RAW)
    assert publicly_available_notice.mets_manifestation is None
    assert publicly_available_notice.rdf_manifestation is None
    assert publicly_available_notice.normalised_metadata is None
    assert publicly_available_notice.xml_manifestation is not None
    assert publicly_available_notice.original_metadata is not None
