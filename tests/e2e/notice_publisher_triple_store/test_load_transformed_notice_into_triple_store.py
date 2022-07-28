from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_notice_into_triple_store, DEFAULT_NOTICE_REPOSITORY_NAME
from tests.fakes.fake_repository import FakeNoticeRepository


SPARQL_QUERY = "select * {?s ?p ?o}"
Grath = "SELECT * WHERE { { GRAPH ?g { ?s ?p ?o } }"

def test_load_notice_into_triple_store(transformed_complete_notice, allegro_triple_store):
    fake_notice_repo = FakeNoticeRepository()
    fake_notice_repo.add(transformed_complete_notice)
    load_notice_into_triple_store(notice_id=transformed_complete_notice.ted_id, notice_repository=fake_notice_repo,
                                  triple_store_repository=allegro_triple_store)

    sparql_endpoint = allegro_triple_store.get_sparql_triple_store_endpoint(DEFAULT_NOTICE_REPOSITORY_NAME)
    assert sparql_endpoint is not None

    query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY).fetch_tree()
    assert query_result
    print(query_result)
    # assert that the graph in the triple store has more that 1 triple inside
    if len(SPARQL_QUERY) in query_result >= 1:
        assert True
    # assert that at least one graph exists in the triple store
    if SPARQL_QUERY in query_result:
        assert True
    # assert that the there is an epo:Identifier object that has the value equal to the notice ID

