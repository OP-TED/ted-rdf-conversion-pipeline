import pytest
from _pytest._code import ExceptionInfo
from pytest_bdd import scenario, given, when, then

from ted_sws.domain.model.notice import Notice
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


@scenario('test_notice_fetcher.feature', 'Fetch a TED notice')
def test_fetch_a_ted_notice():
    """Fetch a TED notice"""


@given("a TED REST API download endpoint", target_fixture="api_url")
def step_impl(api_end_point):
    return api_end_point


@given("correct download API parameters")
def step_impl(notice_search_query):
    return notice_search_query


@when("call to the API is made", target_fixture="api_call")
def step_impl(notice_search_query, api_end_point, fake_notice_storage):
    NoticeFetcher(notice_repository=fake_notice_storage,
        ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    return [fake_notice_storage.get(reference=reference) for reference in fake_notice_storage.list()]


@then("a notice and notice metadata is received from the API", target_fixture="fake_notice_storage")
def step_impl(api_call, fake_notice_storage):
    # TODO remove target fixture and fake notice storage from this step when notice fetcher will have the
    #  storage facility added
    assert isinstance(api_call, list)
    assert len(api_call) > 0
    notice = api_call[0]
    assert isinstance(notice, Notice)
    assert notice.xml_manifestation
    assert notice.original_metadata
    fake_notice_storage.add(notice)
    return fake_notice_storage


@then("the notice and notice metadata are stored")
def step_impl(fake_notice_storage, notice_identifier):
    # TODO replace fake notice storage with real one when it is available
    assert fake_notice_storage.get(reference=notice_identifier)
    assert fake_notice_storage.get(reference=notice_identifier).original_metadata
    assert fake_notice_storage.get(reference=notice_identifier).xml_manifestation


@scenario('test_notice_fetcher.feature', 'Fail to fetch a TED notice')
def test_fail_to_fetch_a_ted_notice():
    """Fail to fetch a TED notice"""


@given("incorrect download API parameters")
def step_impl(notice_incorrect_search_query):
    return notice_incorrect_search_query


@when("the call to the API is made", target_fixture="api_call_message")
def step_impl(notice_incorrect_search_query, api_end_point,fake_notice_storage):
    with pytest.raises(Exception) as e:
        NoticeFetcher(notice_repository=fake_notice_storage,
            ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_end_point)).fetch_notices_by_query(
            query=notice_incorrect_search_query)
    return e


@when("no notice or metadata is returned")
def step_impl(fake_notice_storage, notice_identifier):
    # TODO replace fake notice storage with real one when is available
    assert fake_notice_storage.get(notice_identifier) is None


@then("an error message is received indicating the problem")
def step_impl(api_call_message):
    assert isinstance(api_call_message, ExceptionInfo)
    assert str(api_call_message.value) == "The API call failed with: <Response [500]>"
