import pytest
from pytest_bdd import scenario, given, when, then

from ted_sws.domain.model.notice import Notice
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


@scenario('test_fetching_types.feature', 'Fetch a TED notice by identifier')
def test_fetch_a_ted_notice_by_identifier():
    """fetching a ted notice by identifier"""


@scenario('test_fetching_types.feature', 'Fetch a TED notice by search query')
def test_fetch_a_ted_notice_by_query():
    """fetching a ted notice by search query"""


# STEP implementations

@given("a TED REST API download endpoint", target_fixture="api_url")
def step_impl(api_end_point):
    return api_end_point


@given("a identifier parameter", target_fixture="identifier")
def step_impl(notice_identifier):
    return notice_identifier


@when("the call to the API is made", target_fixture="api_call")
def step_impl(identifier, api_url):
    return NoticeFetcher(
        ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_url)).get_notice_by_id(
        document_id=identifier)


@then("a notice with that identifier and the notice metadata are available", target_fixture="fake_notice_storage")
def step_impl(api_call, fake_notice_storage):
    # TODO remove target fixture and fake notice storage from this step when notice fetcher will have the
    #  storage facility added
    notice = api_call
    assert isinstance(notice, Notice)
    assert notice.original_metadata
    assert notice.xml_manifestation
    fake_notice_storage.add(notice)
    return fake_notice_storage


@then("are stored")
def step_impl(fake_notice_storage, identifier):
    # TODO replace fake notice storage with real one when it is available
    assert fake_notice_storage.get(reference=identifier)


@given("search query")
def step_impl(notice_search_query):
    return notice_search_query


@when("the call to the search API is made", target_fixture="api_call")
def step_impl(notice_search_query, api_end_point):
    return NoticeFetcher(
        ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_end_point)).get_notices_by_query(
        query=notice_search_query)


@then("notices that match the search query result and their metadata are available",
      target_fixture="fake_notice_storage")
def step_impl(api_call, fake_notice_storage, notice_identifier):
    # TODO remove target fixture and fake notice storage from this step when notice fetcher will have the
    #  storage facility added
    assert len(api_call) == 1
    notice = api_call[0]
    assert isinstance(notice, Notice)
    assert notice.ted_id == notice_identifier
    assert notice.original_metadata
    assert notice.xml_manifestation
    fake_notice_storage.add(notice)
    return fake_notice_storage


@then("are stored")
def step_impl(fake_notice_storage, notice_identifier):
    # TODO replace fake notice storage with real one when it is available
    assert fake_notice_storage.get(reference=notice_identifier)
