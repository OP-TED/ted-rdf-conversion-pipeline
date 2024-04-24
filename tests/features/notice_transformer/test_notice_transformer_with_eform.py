"""Notice transformer feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC
from ted_sws.notice_transformer.services.notice_transformer import transform_notice, transform_notice_by_id


@scenario('test_notice_transformer_with_eform.feature', 'Transform a eForm TED notice')
def test_transform_a_ted_notice():
    """Transform a TED notice."""


@given('a mapping suite package')
def a_mapping_suite_package(eform_mapping_suite):
    """a mapping suite package."""
    assert eform_mapping_suite
    assert isinstance(eform_mapping_suite, MappingSuite)


@given('a eForm notice', target_fixture="eligible_for_transformation_eForm_notice")
def a_notice(eform_transformation_eligible_notice):
    """a notice."""
    assert eform_transformation_eligible_notice
    assert isinstance(eform_transformation_eligible_notice, Notice)
    return eform_transformation_eligible_notice


@given('a rml mapper')
def a_rml_mapper(rml_mapper):
    """a rml mapper."""
    assert rml_mapper
    assert isinstance(rml_mapper, RMLMapperABC)


@given('given mapping suite is eligible for notice transformation')
def given_mapping_suite_is_eligible_for_notice_transformation():
    """given mapping suite is eligible for notice transformation."""


@given('given notice is eligible for transformation')
def given_notice_is_eligible_for_transformation(eligible_for_transformation_eForm_notice):
    """given notice is eligible for transformation."""
    assert eligible_for_transformation_eForm_notice
    assert eligible_for_transformation_eForm_notice.status == NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION


@when('the notice transformation is executed', target_fixture="transformed_notice")
def the_notice_transformation_is_executed(eligible_for_transformation_eForm_notice, mapping_suite, rml_mapper):
    """the notice transformation is executed."""
    transformed_notice = transform_notice(notice=eligible_for_transformation_eForm_notice, mapping_suite=mapping_suite,
                                          rml_mapper=rml_mapper)
    return transformed_notice


@then('the notice has RDF manifestation')
def the_notice_have_rdf_manifestation(transformed_notice: Notice):
    """the notice have RDF manifestation."""
    assert transformed_notice.rdf_manifestation
    assert transformed_notice.rdf_manifestation.object_data


@then('the notice status is TRANSFORMED')
def the_notice_status_is_transformed(transformed_notice: Notice):
    """the notice status is TRANSFORMED."""
    assert transformed_notice.status == NoticeStatus.TRANSFORMED
