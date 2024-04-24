from pytest_bdd import scenario, given, when, then, parsers

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice


@scenario('metadata_normaliser_eforms.feature', 'Normalising notice metadata for an eForm')
def test_normalise_metadata():
    """normalising metadata"""


@given("a eForm notice", target_fixture="notice")
def step_impl(eForm_notice_2023):
    return eForm_notice_2023


@when("the normalise process is executed")
def step_impl(notice):
    normalise_notice(notice=notice)


@then(parsers.parse("a normalised notice {metadata} is {possibly} available"))
def step_impl(notice, metadata, possibly):
    metadata_value = notice.normalised_metadata.dict()[metadata]
    print(notice.normalised_metadata)
    print(metadata)
    is_value_there = "True" if metadata_value else "False"
    assert is_value_there == possibly


@then("the notice status is NORMALISED_METADATA")
def step_impl(notice):
    assert notice.status is NoticeStatus.NORMALISED_METADATA


@then("normalised metadata is available")
def step_impl(notice):
    assert notice.normalised_metadata
