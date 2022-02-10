from pytest_bdd import scenario, given, when, then

from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata
from ted_sws.domain.model.notice import Notice


@scenario("test_creating_notice.feature", "Create a bare minimum notice")
def test_Create_a_bare_minimum_notice():
    pass


@given("a TED identifier ted_identifier", target_fixture="ted_identifier")
def step_impl():
    return "ted_identifier_1234"


@given("original TED notice metadata notice_metadata", target_fixture="ted_metadata")
def step_impl():
    return TEDMetadata(**{"AA": "clever value"})


@given("the XML content of the notice xml_content", target_fixture="notice_content")
def step_impl():
    return XMLManifestation(object_data="XML content")


@when("a notice is instantiated", target_fixture="new_notice")
def step_impl(ted_identifier, ted_metadata, notice_content):
    return Notice(ted_id=ted_identifier, original_metadata=ted_metadata,
                  xml_manifestation=notice_content)


@then("a new notice object is available")
def step_impl(new_notice):
    assert new_notice is not None


@then("notice_metadata, xml_content, source_url and status RAW are accessible")
def step_impl(new_notice, ted_identifier, ted_metadata, notice_content):
    assert new_notice.original_metadata == ted_metadata
    assert new_notice.xml_manifestation == notice_content
    assert new_notice.ted_id == ted_identifier

