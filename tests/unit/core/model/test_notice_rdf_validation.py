#!/usr/bin/python3

# test_notice_rdf_validation.py
# Date:  12/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import pytest

from ted_sws.core.model.manifestation import RDFValidationManifestation, SHACLTestSuiteValidationReport, \
    QueriedSHACLShapeValidationResult
from ted_sws.core.model.notice import NoticeStatus


def test_set_notice_rdf_validation(publicly_available_notice, raw_notice):
    shacl_validation = SHACLTestSuiteValidationReport(object_data="this is a shacl validation report",
                                                  test_suite_identifier="shacl_test_suite_id",
                                                  mapping_suite_identifier="mapping_suite_id",
                                                  validation_results=QueriedSHACLShapeValidationResult())

    publicly_available_notice.set_rdf_validation(rdf_validation=shacl_validation)


    publicly_available_notice.set_distilled_rdf_validation(rdf_validation=shacl_validation)
    assert publicly_available_notice.status is NoticeStatus.VALIDATED
    assert publicly_available_notice.mets_manifestation is None

    assert raw_notice.get_distilled_rdf_validation() is None
    assert raw_notice.get_rdf_validation() is None
    with pytest.raises(ValueError):
        raw_notice.set_rdf_validation(shacl_validation)


def test_set_notice_distilled_rdf_validation(publicly_available_notice, raw_notice):
    shacl_validation = SHACLTestSuiteValidationReport(object_data="this is a shacl validation report",
                                                  test_suite_identifier="shacl_test_suite_id",
                                                  mapping_suite_identifier="mapping_suite_id",
                                                  validation_results=QueriedSHACLShapeValidationResult())

    publicly_available_notice.set_distilled_rdf_validation(rdf_validation=shacl_validation)
    publicly_available_notice.set_rdf_validation(rdf_validation=shacl_validation)

    assert publicly_available_notice.status is NoticeStatus.VALIDATED
    assert publicly_available_notice.mets_manifestation is None

    with pytest.raises(ValueError):
        raw_notice.set_distilled_rdf_validation(shacl_validation)
