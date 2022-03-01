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


@when("the call to the API is made", target_fixture="notice_storage")
def step_impl(identifier, api_url, notice_storage):
    NoticeFetcher(notice_repository=notice_storage,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_url)).fetch_notice_by_id(
        document_id=identifier)
    return notice_storage


@then("a notice with that identifier and the notice metadata are available", target_fixture="notice_storage")
def step_impl(identifier, notice_storage):
    notice = notice_storage.get(reference=identifier)
    assert isinstance(notice, Notice)
    assert notice.original_metadata
    assert notice.xml_manifestation
    return notice_storage


@then("are stored")
def step_impl(notice_storage, identifier):
    assert notice_storage.get(reference=identifier)


@given("search query")
def step_impl(notice_search_query):
    return notice_search_query


@when("the call to the search API is made", target_fixture="api_call")
def step_impl(notice_search_query, api_end_point, notice_storage):
    NoticeFetcher(notice_repository=notice_storage,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    return list(notice_storage.list())


@then("notices that match the search query result and their metadata are available",
      target_fixture="notice_storage")
def step_impl(api_call, notice_storage, notice_identifier):
    assert len(api_call) == 1
    notice = api_call[0]
    assert isinstance(notice, Notice)
    assert notice.ted_id == notice_identifier
    assert notice.original_metadata
    assert notice.xml_manifestation
    return notice_storage


@then("are stored")
def step_impl(notice_storage, notice_identifier):
    assert notice_storage.get(reference=notice_identifier)
