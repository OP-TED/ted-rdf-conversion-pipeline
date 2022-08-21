"""Notice fetcher feature tests."""

from datetime import date, datetime

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.notice import Notice, NoticeStatus


@scenario('test_notice_fetcher.feature', 'Fetch a notice by id, from Ted')
def test_fetch_a_notice_by_id_from_ted():
    """Fetch a notice by id, from Ted."""


@scenario('test_notice_fetcher.feature', 'Fetch notices by date range, from Ted')
def test_fetch_notices_by_date_range_from_ted():
    """Fetch notices by date range, from Ted."""


@scenario('test_notice_fetcher.feature', 'Fetch notices by date wild card, from Ted')
def test_fetch_notices_by_date_wild_card_from_ted():
    """Fetch notices by date wild card, from Ted."""


@scenario('test_notice_fetcher.feature', 'Fetch notices by query, from Ted')
def test_fetch_notices_by_query_from_ted():
    """Fetch notices by query, from Ted."""


@given('a date')
def a_date(fetch_date):
    """a date."""
    assert type(fetch_date) == date


@given('a end_date')
def a_end_date(fetch_end_date):
    """a end_date."""
    assert type(fetch_end_date) == date


@given('a notice_id')
def a_notice_id(notice_id):
    """a notice_id."""
    assert type(notice_id) == str


@given('a query')
def a_query(fetch_query):
    """a query."""
    assert type(fetch_query) == dict


@given('a start_date')
def a_start_date(fetch_start_date):
    """a start_date."""
    assert type(fetch_start_date) == date


@given('a wildcard_date')
def a_wildcard_date(fetch_wildcard_date):
    """a wildcard_date."""
    assert type(fetch_wildcard_date) == str
    date_filter = datetime.strptime(fetch_wildcard_date, "%Y%m%d*").date()
    assert type(date_filter) == date


@given('knowing database endpoint')
def knowing_database_endpoint(mongodb_end_point):
    """knowing database endpoint."""
    assert mongodb_end_point is not None
    assert type(mongodb_end_point) == str


@given('knowing the TED API endpoint')
def knowing_the_ted_api_endpoint(ted_api_end_point):
    """knowing the TED API endpoint."""
    assert ted_api_end_point is not None
    assert type(ted_api_end_point) == str


@when('notice fetching by date wildcard is executed', target_fixture="fetched_notice_ids")
def notice_fetching_by_date_wildcard_is_executed(notice_fetcher, fetch_wildcard_date):
    """notice fetching by date wildcard is executed."""
    notice_ids = notice_fetcher.fetch_notices_by_date_wild_card(wildcard_date=fetch_wildcard_date)
    return notice_ids


@when('notice fetching by id is executed')
def notice_fetching_by_id_is_executed(notice_fetcher, fetch_notice_id, notice_repository):
    """notice fetching by id is executed."""
    notice_fetcher.fetch_notice_by_id(document_id=fetch_notice_id)


@when('notices fetching by date range is executed', target_fixture="fetched_notice_ids")
def notices_fetching_by_date_range_is_executed(notice_fetcher, fetch_start_date, fetch_end_date):
    """notices fetching by date range is executed."""
    notice_ids = notice_fetcher.fetch_notices_by_date_range(start_date=fetch_start_date, end_date=fetch_end_date)
    return notice_ids


@when('notices fetching by date wild card is executed', target_fixture="fetched_notice_ids")
def notices_fetching_by_date_wild_card_is_executed(notice_fetcher, fetch_wildcard_date):
    """notices fetching by date wild card is executed."""
    notice_ids = notice_fetcher.fetch_notices_by_date_wild_card(wildcard_date=fetch_wildcard_date)
    return notice_ids


@when('notices fetching by query is executed', target_fixture="fetched_notice_ids")
def notices_fetching_by_query_is_executed(notice_fetcher, fetch_query):
    """notices fetching by query is executed."""
    notice_ids = notice_fetcher.fetch_notices_by_query(query=fetch_query)
    return notice_ids


@then('a list of fetched notice_ids is returned')
def a_list_of_fetched_notice_ids_is_returned(fetched_notice_ids):
    """a list of fetched notice_ids is returned."""
    assert fetched_notice_ids is not None
    assert type(fetched_notice_ids) == list
    for notice_id in fetched_notice_ids:
        assert type(notice_id) == str


@then('fetched notice have original_metadata')
def fetched_notice_have_original_metadata(fetched_notice: Notice):
    """fetched notice have original_metadata."""
    assert fetched_notice.original_metadata


@then('fetched notice have raw status')
def fetched_notice_have_raw_status(fetched_notice: Notice):
    """fetched notice have raw status."""
    assert fetched_notice.status == NoticeStatus.RAW


@then('fetched notice have xml_manifestation')
def fetched_notice_have_xml_manifestation(fetched_notice: Notice):
    """fetched notice have xml_manifestation."""
    assert fetched_notice.xml_manifestation
    assert fetched_notice.xml_manifestation.object_data


@then('fetched notice is available in database', target_fixture="fetched_notice")
def fetched_notice_is_available_in_database(fetch_notice_id, notice_repository):
    """fetched notice is available in database."""
    result_notice = notice_repository.get(reference=fetch_notice_id)
    assert result_notice
    return result_notice


@then('foreach returned notice_id exist in database a notice with RAW status')
def foreach_returned_notice_id_exist_in_database_a_notice_with_raw_status(fetched_notice_ids, notice_repository):
    """foreach returned notice_id exist in database a notice with RAW status."""
    for notice_id in fetched_notice_ids:
        notice = notice_repository.get(reference=notice_id)
        assert notice
        assert notice.status == NoticeStatus.RAW


@then('foreach returned notice_id exist in database a notice with original_metadata')
def foreach_returned_notice_id_exist_in_database_a_notice_with_original_metadata(fetched_notice_ids, notice_repository):
    """foreach returned notice_id exist in database a notice with original_metadata."""
    for notice_id in fetched_notice_ids:
        notice = notice_repository.get(reference=notice_id)
        assert notice
        assert notice.original_metadata


@then('foreach returned notice_id exist in database a notice with xml_manifestation')
def foreach_returned_notice_id_exist_in_database_a_notice_with_xml_manifestation(fetched_notice_ids, notice_repository):
    """foreach returned notice_id exist in database a notice with xml_manifestation."""
    for notice_id in fetched_notice_ids:
        notice = notice_repository.get(reference=notice_id)
        assert notice
        assert notice.xml_manifestation
        assert notice.xml_manifestation.object_data
