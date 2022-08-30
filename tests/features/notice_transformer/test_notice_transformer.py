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


@scenario('test_notice_transformer.feature', 'Transform a TED notice')
def test_transform_a_ted_notice():
    """Transform a TED notice."""


@scenario('test_notice_transformer.feature', 'Transform a TED notice by id')
def test_transform_a_ted_notice_by_id():
    """Transform a TED notice by id."""


@given('a mapping suite package')
def a_mapping_suite_package(mapping_suite):
    """a mapping suite package."""
    assert mapping_suite
    assert isinstance(mapping_suite, MappingSuite)


@given('a mapping suite package id')
def a_mapping_suite_package_id(mapping_suite_id):
    """a mapping suite package id."""
    assert mapping_suite_id
    assert type(mapping_suite_id) == str


@given('a mapping suite repository')
def a_mapping_suite_repository(mapping_suite_repository):
    """a mapping suite repository."""
    assert mapping_suite_repository
    assert isinstance(mapping_suite_repository, MappingSuiteRepositoryABC)


@given('a notice', target_fixture="eligible_for_transformation_notice")
def a_notice(transformation_eligible_notice):
    """a notice."""
    assert transformation_eligible_notice
    assert isinstance(transformation_eligible_notice, Notice)
    return transformation_eligible_notice


@given('a notice id', target_fixture="eligible_for_transformation_notice")
def a_notice_id(notice_id, transformation_eligible_notice, notice_repository):
    """a notice id."""
    assert notice_id
    assert type(notice_id) == str
    notice_repository.add(notice=transformation_eligible_notice)
    return transformation_eligible_notice


@given('a notice repository')
def a_notice_repository(notice_repository):
    """a notice repository."""
    assert notice_repository
    assert isinstance(notice_repository, NoticeRepositoryABC)


@given('a rml mapper')
def a_rml_mapper(rml_mapper):
    """a rml mapper."""
    assert rml_mapper
    assert isinstance(rml_mapper, RMLMapperABC)


@given('given mapping suite is eligible for notice transformation')
def given_mapping_suite_is_eligible_for_notice_transformation():
    """given mapping suite is eligible for notice transformation."""


@given('given notice is eligible for transformation')
def given_notice_is_eligible_for_transformation(eligible_for_transformation_notice):
    """given notice is eligible for transformation."""
    assert eligible_for_transformation_notice
    assert eligible_for_transformation_notice.status == NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION


@when('the notice transformation is executed', target_fixture="transformed_notice")
def the_notice_transformation_is_executed(eligible_for_transformation_notice, mapping_suite, rml_mapper):
    """the notice transformation is executed."""
    transformed_notice = transform_notice(notice=eligible_for_transformation_notice, mapping_suite=mapping_suite,
                                          rml_mapper=rml_mapper)
    return transformed_notice


@when('the notice transformation by id is executed', target_fixture="notice_repository_with_transformed_notice")
def the_notice_transformation_by_id_is_executed(notice_id, mapping_suite_id, notice_repository,
                                                mapping_suite_repository, rml_mapper):
    """the notice transformation is executed."""
    transform_notice_by_id(notice_id=notice_id, mapping_suite_id=mapping_suite_id, notice_repository=notice_repository,
                           mapping_suite_repository=mapping_suite_repository, rml_mapper=rml_mapper)
    return notice_repository


@then('the RDF notice manifestation is available in the database', target_fixture="transformed_notice")
def the_rdf_notice_manifestation_is_available_in_the_database(notice_id: str,
                                                              notice_repository_with_transformed_notice: NoticeRepositoryABC):
    """the RDF notice manifestation is available in the database."""
    notice = notice_repository_with_transformed_notice.get(reference=notice_id)
    assert notice
    assert notice.rdf_manifestation
    assert notice.rdf_manifestation.object_data
    return notice


@then('the notice have RDF manifestation')
def the_notice_have_rdf_manifestation(transformed_notice: Notice):
    """the notice have RDF manifestation."""
    assert transformed_notice.rdf_manifestation
    assert transformed_notice.rdf_manifestation.object_data


@then('the notice status is TRANSFORMED')
def the_notice_status_is_transformed(transformed_notice: Notice):
    """the notice status is TRANSFORMED."""
    assert transformed_notice.status == NoticeStatus.TRANSFORMED
