"""Notice metadata processor feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from src.ted_sws.core.model.notice import Notice, NoticeStatus
from src.ted_sws.data_manager.adapters.repository_abc import MappingPackageRepositoryABC
from src.ted_sws.notice_metadata_processor.services.notice_eligibility import notice_eligibility_checker


@scenario('test_eForm_notice_eligibility.feature', 'Notice eligibility checking for eForms')
def test_notice_eligibility_checking_positive():
    """Notice eligibility checking positive."""


@given('a mapping suite for eforms subtype 16 and sdk version 1.7 is available in mapping suite repository', target_fixture="mapping_package_repository")
def a_mapping_package_for_f03_is_available_in_mapping_package_repository(clean_mapping_package_repository,
                                                                     mapping_package_repository_with_mapping_package):
    """a mapping suite for eforms subtype 16 and sdk version 1.7 is available in mapping suite repository."""
    for mapping_package in mapping_package_repository_with_mapping_package.list():
        clean_mapping_package_repository.add(mapping_package=mapping_package)
    return clean_mapping_package_repository



@given('a mapping suite repository')
def a_mapping_package_repository(clean_mapping_package_repository):
    """a mapping suite repository."""
    assert clean_mapping_package_repository
    assert isinstance(clean_mapping_package_repository, MappingPackageRepositoryABC)


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
def the_notice_eligibility_checking_is_executed(normalised_eForm_notice, mapping_package_repository):
    """the notice eligibility checking is executed."""
    notice_eligibility_checker(notice=normalised_eForm_notice, mapping_package_repository=mapping_package_repository)
    return normalised_eForm_notice


@then('the notice status is ELIGIBLE_FOR_TRANSFORMATION')
def the_notice_status_is_eligible_for_transformation(checked_notice: Notice):
    """the notice status is ELIGIBLE_FOR_TRANSFORMATION."""
    assert checked_notice.status == NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION

