from pytest_bdd import scenario, given, when, then

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.metadata_normaliser.services.metadata_normalizer import MetadataNormaliser
from ted_sws.notice_eligibility.services.notice_eligibility import notice_eligibility_checker


@scenario('test_notice_eligibility_validation_tests.feature', 'not finding validation tests set for a TED XML notice')
def test_ineligibility():
    """not finding validation tests set for a TED XML notice"""


@given("a notice", target_fixture="ineligibility_notice")
def step_impl(f18_notice_2022):
    return f18_notice_2022


@when("checking process is executed", target_fixture="ineligibility_result")
def step_impl(ineligibility_notice, notice_storage, mapping_suite_repository_in_file_system):
    MetadataNormaliser(notice=ineligibility_notice).normalise_metadata()
    return notice_eligibility_checker(notice=ineligibility_notice,
                                      mapping_suite_repository=mapping_suite_repository_in_file_system)


@then("validation tests set is not found")
def step_impl(ineligibility_result):
    assert ineligibility_result is None


@then("notice status INELIGIBLE_FOR_TRANSFORMATION")
def step_impl(ineligibility_notice):
    assert ineligibility_notice.status == NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION
