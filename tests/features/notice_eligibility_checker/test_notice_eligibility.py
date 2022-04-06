from pytest_bdd import scenario, given, when, then

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.metadata_normaliser.services.metadata_normalizer import MetadataNormaliser
from ted_sws.notice_eligibility.services.notice_eligibility import notice_eligibility_checker


@scenario('test_notice_eligibility_validation_tests.feature', 'Find validation test set for a TED XML notice')
def test_eligibility():
    """Find validation test set for a TED XML notice"""


@given("a notice", target_fixture="notice")
def step_impl(f03_notice_2020):
    return f03_notice_2020


@when("checking process is executed", target_fixture="eligibility_result")
def step_impl(notice, notice_storage, mapping_suite_repository_in_file_system):
    MetadataNormaliser(notice=notice).normalise_metadata()
    return notice_eligibility_checker(notice=notice, mapping_suite_repository=mapping_suite_repository_in_file_system)


@then("a validation test set is found")
def step_impl(eligibility_result):
    assert isinstance(eligibility_result, tuple)
    assert "test_package2" in eligibility_result
    assert "408313-2020" in eligibility_result


@then("notice status ELIGIBLE_FOR_TRANSFORMATION")
def step_impl(notice):
    assert notice.status == NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION



