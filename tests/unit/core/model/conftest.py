#!/usr/bin/python3

# conftest.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest

from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation, \
    SHACLTestSuiteValidationReport, SPARQLTestSuiteValidationReport, \
    XPATHCoverageValidationReport
from ted_sws.core.model.metadata import TEDMetadata, NormalisedMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus


@pytest.fixture
def fetched_notice_data():
    ted_id = "ted_id1"
    original_metadata = TEDMetadata(**{"AA": ["Value here"]})
    xml_manifestation = XMLManifestation(object_data="XML manifestation content")
    return ted_id, original_metadata, xml_manifestation


@pytest.fixture(scope="function")
def publicly_available_notice(fetched_notice_data, normalised_metadata_dict) -> Notice:
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    sparql_validation = SPARQLTestSuiteValidationReport(object_data="This is validation report!",
                                                        test_suite_identifier="sparql_test_id",
                                                        mapping_suite_identifier="mapping_suite_id",
                                                        validation_results=[])
    shacl_validation = SHACLTestSuiteValidationReport(object_data="This is validation report!",
                                                      test_suite_identifier="shacl_test_id",
                                                      mapping_suite_identifier="mapping_suite_id",
                                                      validation_results=[])
    xpath_coverage_validation = XPATHCoverageValidationReport(object_data="This is validation report!",
                                                              test_suite_identifier="shacl_test_id",
                                                              mapping_suite_identifier="mapping_suite_id",
                                                              validation_result=None)
    notice = Notice(ted_id=ted_id)
    notice.set_xml_manifestation(xml_manifestation)
    notice.set_original_metadata(original_metadata)
    notice._status = NoticeStatus.INDEXED
    notice.set_normalised_metadata(NormalisedMetadata(**normalised_metadata_dict))
    notice._status = NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION
    notice.set_preprocessed_xml_manifestation(xml_manifestation)
    notice._status = NoticeStatus.DISTILLED
    notice.set_rdf_manifestation(RDFManifestation(object_data="RDF manifestation content",
                                                  shacl_validations=[shacl_validation],
                                                  sparql_validations=[sparql_validation],
                                                  xpath_coverage_validation=xpath_coverage_validation
                                                  ))
    notice.set_distilled_rdf_manifestation(RDFManifestation(object_data="RDF manifestation content",
                                                            shacl_validations=[shacl_validation],
                                                            sparql_validations=[sparql_validation],
                                                            xpath_coverage_validation=xpath_coverage_validation
                                                            ))
    notice._status = NoticeStatus.ELIGIBLE_FOR_PACKAGING
    notice.set_mets_manifestation(METSManifestation(object_data="METS manifestation content"))
    notice._status = NoticeStatus.PUBLICLY_AVAILABLE
    return notice


@pytest.fixture(scope="function")
def raw_notice(fetched_notice_data) -> Notice:
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    notice = Notice(ted_id=ted_id)
    notice.set_xml_manifestation(xml_manifestation)
    notice.set_original_metadata(original_metadata)
    return notice


@pytest.fixture(scope="function")
def transformation_eligible_notice(indexed_notice) -> Notice:
    indexed_notice.set_normalised_metadata(normalised_metadata=NormalisedMetadata(**{"AA": "notice metadata "}))
    indexed_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    return indexed_notice
