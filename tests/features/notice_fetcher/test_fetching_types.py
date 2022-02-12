from pytest_bdd import scenario, given, when, then, scenarios


@scenario("test_fetching_types.feature", "Fetch a TED notice by identifier", )
def test_fetch_notice_by_identifier():
    pass


@scenario("test_fetching_types.feature", "Fetch a TED notice by search query")
def test_fetch_notice_by_search_query():
    pass


@given("a TED REST API download endpoint")
def step_impl():
    print(u'STEP: Given a TED REST API download endpoint')


@given("a identifier parameter")
def step_impl():
    print(u'STEP: And a identifier parameter')


@when("the call to the API is made")
def step_impl():
    print(u'STEP: When the call to the API is made')


@then("a notice with that identifier and the notice metadata are available")
def step_impl():
    print(u'STEP: Then a notice with that identifier and the notice metadata are available')


@then("are stored")
def step_impl():
    print(u'STEP: And are stored')


@given("search result set")
def step_impl():
    print(u'STEP: And search result set')


@then("notice(s) that match the search query result and their metadata are available")
def step_impl():
    print(
        u'STEP: Then notice(s) that match the search query result and their metadata are available')

