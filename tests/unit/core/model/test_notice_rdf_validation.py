#!/usr/bin/python3

# test_notice_rdf_validation.py
# Date:  12/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import pytest

from ted_sws.core.model.manifestation import RDFValidationManifestation
from ted_sws.core.model.notice import NoticeStatus, UnsupportedStatusTransition


def test_set_notice_rdf_validation(publicly_available_notice, raw_notice):
    validation = RDFValidationManifestation(object_data="this is a new validation report")
    publicly_available_notice.set_rdf_validation(
        rdf_validation=validation)
    assert publicly_available_notice.status is NoticeStatus.VALIDATED
    assert publicly_available_notice.mets_manifestation is None

    with pytest.raises(ValueError):
        raw_notice.set_rdf_validation(validation)
