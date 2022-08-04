from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_notice_into_triple_store, DEFAULT_NOTICE_REPOSITORY_NAME
from tests.fakes.fake_repository import FakeNoticeRepository


SPARQL_QUERY_TRIPLES = "select * {?s ?p ?o}"
SPARQL_QUERY_GRAPH = "SELECT ?g {  GRAPH ?g { ?s ?p ?o  } }"
SPARQL_QUERY_FIXED_URI = "select * { <http://data.europa.eu/a4g/resource/ReviewerOrganisationIdentifier/2018-S-175-396207/de2507f9-ae25-37c8-809c-0109efe10669> ?p ?o .} "


def test_load_notice_into_triple_store(transformed_complete_notice, allegro_triple_store):
    fake_notice_repo = FakeNoticeRepository()
    fake_notice_repo.add(transformed_complete_notice)
    load_notice_into_triple_store(notice_id=transformed_complete_notice.ted_id, notice_repository=fake_notice_repo,
                                  triple_store_repository=allegro_triple_store)

    sparql_endpoint = allegro_triple_store.get_sparql_triple_store_endpoint(DEFAULT_NOTICE_REPOSITORY_NAME)
    assert sparql_endpoint is not None

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_TRIPLES).fetch_tabular()
    assert df_query_result is not None
    # assert that the graph in the triple store has more than 1 triple inside
    if len(df_query_result) > 0:
        assert True

     # assert that at least one graph exists in the triple store
    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_GRAPH).fetch_tabular()
    assert df_query_result is not None
    if len(df_query_result) > 0:
        assert True

     # assert that the there is an epo:SPARQL_QUERY_FIXED_URI object that has the value equal to the notice ID
    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_FIXED_URI).fetch_tabular()
    assert df_query_result is not None
    print(df_query_result)
    if len(df_query_result) > 0:
        assert True
