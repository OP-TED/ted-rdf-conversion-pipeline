from pytest_bdd import scenario, given, when, then, parsers

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice


@scenario('metadata_normaliser.feature', 'Normalizing a notice metadata')
def test_extract_metadata():
    """normalising metadata"""


@given("a notice", target_fixture="notice")
def step_impl(f03_notice_2020):
    return f03_notice_2020


@when("the normalize process is executed")
def step_impl(notice):
    normalise_notice(notice=notice)


@then(parsers.parse("a normalized notice {metadata} is {possibly} available"))
def step_impl(notice, metadata, possibly):
    metadata_value = notice.normalised_metadata.dict()[metadata]
    is_value_there = "True" if metadata_value else "False"
    assert is_value_there == possibly


@then("the notice status is NORMALISED_METADATA")
def step_impl(notice):
    assert notice.status is NoticeStatus.NORMALISED_METADATA


@then("normalised metadata is available")
def step_impl(notice):
    assert notice.normalised_metadata
