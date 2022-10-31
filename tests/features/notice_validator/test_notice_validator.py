"""Notice Validator feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.manifestation import SHACLTestSuiteValidationReport, \
    SPARQLTestSuiteValidationReport
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.core.model.transform import MappingSuite
from ted_sws.notice_validator.services.shacl_test_suite_runner import validate_notice_with_shacl_suite
from ted_sws.notice_validator.services.sparql_test_suite_runner import validate_notice_with_sparql_suite


@scenario('test_notice_validator.feature', 'SHACL validation')
def test_shacl_validation():
    """SHACL validation."""


@scenario('test_notice_validator.feature', 'SPARQL validation')
def test_sparql_validation():
    """SPARQL validation."""


@given('a mapping suite package')
def a_mapping_suite_package(mapping_suite):
    """a mapping suite package."""
    assert mapping_suite
    assert isinstance(mapping_suite, MappingSuite)


@given('a notice')
def a_notice(notice_with_distilled_status):
    """a notice."""
    assert notice_with_distilled_status
    assert isinstance(notice_with_distilled_status, Notice)


@given('at least one SHACL test suite is available')
def at_least_one_shacl_test_suite_is_available(mapping_suite):
    """at least one SHACL test suite is available."""
    assert mapping_suite.shacl_test_suites
    assert len(mapping_suite.shacl_test_suites)


@given('at least one SPARQL test suite is available')
def at_least_one_sparql_test_suite_is_available(mapping_suite):
    """at least one SPARQL test suite is available."""
    assert mapping_suite.sparql_test_suites
    assert len(mapping_suite.sparql_test_suites)


@given('the notice status is DISTILLED')
def the_notice_status_is_distilled(notice_with_distilled_status):
    """the notice status is DISTILLED."""
    assert notice_with_distilled_status.status == NoticeStatus.DISTILLED


@when('the notice shacl validation is executed', target_fixture="shacl_validated_notice")
def the_notice_shacl_validation_is_executed(notice_with_distilled_status, mapping_suite):
    """the notice shacl validation is executed."""
    validate_notice_with_shacl_suite(notice=notice_with_distilled_status, mapping_suite_package=mapping_suite)
    return notice_with_distilled_status


@when('the notice sparql validation is executed', target_fixture="sparql_validated_notice")
def the_notice_sparql_validation_is_executed(notice_with_distilled_status, mapping_suite):
    """the notice sparql validation is executed."""
    validate_notice_with_sparql_suite(notice=notice_with_distilled_status, mapping_suite_package=mapping_suite)
    return notice_with_distilled_status


@then('the notice have SHACL validation reports for each RDF manifestation')
def the_notice_have_shacl_validation_reports_for_each_rdf_manifestation(shacl_validated_notice):
    """the notice have SHACL validation reports for each RDF manifestation."""
    notice = shacl_validated_notice
    # rdf_validation = notice.get_rdf_validation()
    distilled_rdf_validation = notice.get_distilled_rdf_validation()
    assert notice.status == NoticeStatus.DISTILLED
    # assert isinstance(rdf_validation, list)
    # assert len(rdf_validation) == 1
    # assert isinstance(rdf_validation[0], SHACLTestSuiteValidationReport)
    # assert rdf_validation[0].object_data
    # assert rdf_validation[0].validation_results
    assert isinstance(distilled_rdf_validation, list)
    assert len(distilled_rdf_validation) == 1
    assert isinstance(distilled_rdf_validation[0], SHACLTestSuiteValidationReport)
    assert distilled_rdf_validation[0].object_data
    assert distilled_rdf_validation[0].validation_results


@then('the notice have SPARQL validation reports for each RDF manifestation')
def the_notice_have_sparql_validation_reports_for_each_rdf_manifestation(sparql_validated_notice):
    """the notice have SPARQL validation reports for each RDF manifestation."""
    notice = sparql_validated_notice
    # rdf_validation = notice.get_rdf_validation()
    distilled_rdf_validation = notice.get_distilled_rdf_validation()
    assert notice.status == NoticeStatus.DISTILLED
    # assert isinstance(rdf_validation, list)
    # assert len(rdf_validation) == 1
    # assert isinstance(rdf_validation[0], SPARQLTestSuiteValidationReport)
    # assert rdf_validation[0].object_data
    # assert rdf_validation[0].validation_results
    assert isinstance(distilled_rdf_validation, list)
    assert len(distilled_rdf_validation) == 1
    assert isinstance(distilled_rdf_validation[0], SPARQLTestSuiteValidationReport)
    assert distilled_rdf_validation[0].object_data
    assert distilled_rdf_validation[0].validation_results
