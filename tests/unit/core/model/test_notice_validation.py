#!/usr/bin/python3

# test_notice_rdf_validation.py
# Date:  12/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

from ted_sws.core.model.manifestation import XPATHCoverageValidationReport, SHACLTestSuiteValidationReport, \
    QueriedSHACLShapeValidationResult, RDFManifestation
from ted_sws.core.model.notice import NoticeStatus


def test_set_notice_validation(publicly_available_notice):
    shacl_validation = SHACLTestSuiteValidationReport(object_data="this is a shacl validation report",
                                                      test_suite_identifier="shacl_test_suite_id",
                                                      mapping_suite_identifier="mapping_suite_id",
                                                      validation_results=QueriedSHACLShapeValidationResult())

    publicly_available_notice.set_rdf_validation(rdf_validation=shacl_validation)
    publicly_available_notice.set_distilled_rdf_validation(rdf_validation=shacl_validation)

    publicly_available_notice.set_xml_validation(XPATHCoverageValidationReport(
        object_data="",
        mapping_suite_identifier=""
    ))

    publicly_available_notice.set_rdf_validation(rdf_validation=shacl_validation)
    publicly_available_notice.set_distilled_rdf_validation(rdf_validation=shacl_validation)

    assert publicly_available_notice.status is NoticeStatus.VALIDATED
    assert publicly_available_notice.mets_manifestation is None


def test_set_notice_xml_validation(publicly_available_notice):
    xml_validation = XPATHCoverageValidationReport(
        object_data="",
        mapping_suite_identifier=""
    )

    xml_manifestation = publicly_available_notice.xml_manifestation
    xml_manifestation.add_validation(xml_validation)
    assert xml_manifestation.xpath_coverage_validation
    xml_validations = publicly_available_notice.get_xml_validation()
    assert len(xml_validations)
    assert xml_validation in xml_validations
