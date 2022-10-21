import rdflib
from rdflib.compare import similar
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_rdf_fragment_by_cet_uri_from_notice, \
    write_rdf_fragments_in_triple_store

TMP_TEST_REPOSITORY_NAME = "tmp_test_repository"
TEST_QUERY = "construct {?s ?p ?o .} where {?s ?p ?o .}"

def test_write_rdf_fragments_in_triple_store(notice_with_rdf_manifestation, organisation_cet_uri):
    rdf_fragments = get_rdf_fragment_by_cet_uri_from_notice(notice=notice_with_rdf_manifestation,
                                                            cet_uri=organisation_cet_uri
                                                            )
    assert len(rdf_fragments) == 51
    for rdf_fragment in rdf_fragments:
        assert type(rdf_fragment) == rdflib.Graph

    fuseki_triple_store = FusekiAdapter()
    if TMP_TEST_REPOSITORY_NAME not in fuseki_triple_store.list_repositories():
        fuseki_triple_store.create_repository(repository_name=TMP_TEST_REPOSITORY_NAME)

    write_rdf_fragments_in_triple_store(rdf_fragments=rdf_fragments, triple_store=fuseki_triple_store,
                                        repository_name=TMP_TEST_REPOSITORY_NAME)

    sparql_endpoint = fuseki_triple_store.get_sparql_triple_store_endpoint(repository_name=TMP_TEST_REPOSITORY_NAME)

    initial_graph = rdflib.Graph()
    for rdf_fragment in rdf_fragments:
        initial_graph += rdf_fragment

    result_graph = sparql_endpoint.with_query(sparql_query=TEST_QUERY).fetch_rdf()
    assert isinstance(result_graph, rdflib.Graph)
    assert similar(result_graph, initial_graph)

    fuseki_triple_store.delete_repository(repository_name=TMP_TEST_REPOSITORY_NAME)
