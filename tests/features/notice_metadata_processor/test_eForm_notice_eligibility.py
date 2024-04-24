"""Notice metadata processor feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.notice_metadata_processor.services.notice_eligibility import notice_eligibility_checker


@scenario('test_eForm_notice_eligibility.feature', 'Notice eligibility checking for eForms')
def test_notice_eligibility_checking_positive():
    """Notice eligibility checking positive."""


@given('a mapping suite for eforms subtype 16 and sdk version 1.7 is available in mapping suite repository', target_fixture="mapping_suite_repository")
def a_mapping_suite_for_f03_is_available_in_mapping_suite_repository(clean_mapping_suite_repository,
                                                                     mapping_suite_repository_with_mapping_suite):
    """a mapping suite for eforms subtype 16 and sdk version 1.7 is available in mapping suite repository."""
    for mapping_suite in mapping_suite_repository_with_mapping_suite.list():
        clean_mapping_suite_repository.add(mapping_suite=mapping_suite)
    return clean_mapping_suite_repository



@given('a mapping suite repository')
def a_mapping_suite_repository(clean_mapping_suite_repository):
    """a mapping suite repository."""
    assert clean_mapping_suite_repository
    assert isinstance(clean_mapping_suite_repository, MappingSuiteRepositoryABC)


@given('a notice')
def a_notice(normalised_eForm_notice):
    """a notice."""
    assert normalised_eForm_notice
    assert isinstance(normalised_eForm_notice, Notice)


@given('the notice has eforms subtype 16 and sdk version 1.7')
def the_notice_has_eforms_subtype_and_sdk_version(normalised_eForm_notice):
    """the notice has eforms subtype 16 and sdk version 1.7"""
    assert normalised_eForm_notice.normalised_metadata.eforms_subtype == "16"
    assert normalised_eForm_notice.normalised_metadata.eform_sdk_version == "eforms-sdk-1.7"


@given('the notice status is NORMALISED')
def the_notice_status_is_normalised(normalised_eForm_notice):
    """the notice status is NORMALISED."""
    assert normalised_eForm_notice.status == NoticeStatus.NORMALISED_METADATA


@when('the notice eligibility checking is executed', target_fixture="checked_notice")
def the_notice_eligibility_checking_is_executed(normalised_eForm_notice, mapping_suite_repository):
    """the notice eligibility checking is executed."""
    notice_eligibility_checker(notice=normalised_eForm_notice, mapping_suite_repository=mapping_suite_repository)
    return normalised_eForm_notice


@then('the notice status is ELIGIBLE_FOR_TRANSFORMATION')
def the_notice_status_is_eligible_for_transformation(checked_notice: Notice):
    """the notice status is ELIGIBLE_FOR_TRANSFORMATION."""
    assert checked_notice.status == NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION

