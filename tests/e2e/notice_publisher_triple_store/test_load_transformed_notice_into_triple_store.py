from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_rdf_manifestation_into_triple_store

SPARQL_QUERY_TRIPLES = "select * {?s ?p ?o}"
SPARQL_QUERY_GRAPH = "SELECT ?g {  GRAPH ?g { ?s ?p ?o  } }"
SPARQL_QUERY_FIXED_URI = "select * { <http://data.europa.eu/a4g/resource/ReviewerOrganisationIdentifier/2018-S-175-396207/de2507f9-ae25-37c8-809c-0109efe10669> ?p ?o .} "
TMP_FUSEKI_DATASET_NAME = "tmp_dataset_for_tests"

def test_load_notice_into_triple_store(transformed_complete_notice, fuseki_triple_store):
    fuseki_triple_store.create_repository(repository_name=TMP_FUSEKI_DATASET_NAME)
    load_rdf_manifestation_into_triple_store(rdf_manifestation=transformed_complete_notice.distilled_rdf_manifestation,
                                             triple_store_repository=fuseki_triple_store,
                                             repository_name=TMP_FUSEKI_DATASET_NAME)

    sparql_endpoint = fuseki_triple_store.get_sparql_triple_store_endpoint(TMP_FUSEKI_DATASET_NAME)
    assert sparql_endpoint is not None

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_TRIPLES).fetch_tabular()
    assert df_query_result is not None
    assert len(df_query_result) > 0

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_GRAPH).fetch_tree()
    assert df_query_result is not None
    assert len(df_query_result) > 0

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_FIXED_URI).fetch_tabular()
    assert df_query_result is not None
    assert len(df_query_result) > 0
    
    fuseki_triple_store.delete_repository(repository_name=TMP_FUSEKI_DATASET_NAME)
