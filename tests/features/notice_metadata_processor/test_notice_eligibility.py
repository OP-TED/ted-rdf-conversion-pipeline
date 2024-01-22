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


@scenario('test_notice_eligibility.feature', 'Notice eligibility checking negative')
def test_notice_eligibility_checking_negative():
    """Notice eligibility checking negative."""


@scenario('test_notice_eligibility.feature', 'Notice eligibility checking positive')
def test_notice_eligibility_checking_positive():
    """Notice eligibility checking positive."""


@given('a mapping suite for F03 is available in mapping suite repository', target_fixture="mapping_suite_repository")
def a_mapping_suite_for_f03_is_available_in_mapping_suite_repository(clean_mapping_suite_repository,
                                                                     mapping_suite_repository_with_mapping_suite):
    """a mapping suite for F03 is available in mapping suite repository."""
    for mapping_suite in mapping_suite_repository_with_mapping_suite.list():
        clean_mapping_suite_repository.add(mapping_suite=mapping_suite)
    return clean_mapping_suite_repository


@given('a mapping suite for F03 is not available in mapping suite repository',
       target_fixture="mapping_suite_repository")
def a_mapping_suite_for_f03_is_not_available_in_mapping_suite_repository(clean_mapping_suite_repository):
    """a mapping suite for F03 is not available in mapping suite repository."""
    return clean_mapping_suite_repository


@given('a mapping suite repository')
def a_mapping_suite_repository(clean_mapping_suite_repository):
    """a mapping suite repository."""
    assert clean_mapping_suite_repository
    assert isinstance(clean_mapping_suite_repository, MappingSuiteRepositoryABC)


@given('a notice')
def a_notice(normalised_notice):
    """a notice."""
    assert normalised_notice
    assert isinstance(normalised_notice, Notice)


@given('the notice is with form number F03')
def the_notice_is_with_form_number_f03(normalised_notice):
    """the notice is with form number F03."""
    print(normalised_notice.normalised_metadata)
    assert normalised_notice.normalised_metadata.form_number == "F03"


@given('the notice status is NORMALISED')
def the_notice_status_is_normalised(normalised_notice):
    """the notice status is NORMALISED."""
    assert normalised_notice.status == NoticeStatus.NORMALISED_METADATA


@when('the notice eligibility checking is executed', target_fixture="checked_notice")
def the_notice_eligibility_checking_is_executed(normalised_notice, mapping_suite_repository):
    """the notice eligibility checking is executed."""
    notice_eligibility_checker(notice=normalised_notice, mapping_suite_repository=mapping_suite_repository)
    return normalised_notice


@then('the notice status is ELIGIBLE_FOR_TRANSFORMATION')
def the_notice_status_is_eligible_for_transformation(checked_notice: Notice):
    """the notice status is ELIGIBLE_FOR_TRANSFORMATION."""
    assert checked_notice.status == NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION


@then('the notice status is INELIGIBLE_FOR_TRANSFORMATION')
def the_notice_status_is_ineligible_for_transformation(checked_notice: Notice):
    """the notice status is INELIGIBLE_FOR_TRANSFORMATION."""
    assert checked_notice.status == NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION
