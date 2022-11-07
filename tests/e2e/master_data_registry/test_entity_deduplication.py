from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_entities_by_cet_uri

TEST_MDR_REPOSITORY = "tmp_mdr_test_repository"
TEST_QUERY_UNIQUE_NAMES = """SELECT distinct ?name
WHERE { ?s a <http://www.w3.org/ns/org#Organization> .
?s <http://www.meaningfy.ws/mdr#isCanonicalEntity> True .
?s <http://data.europa.eu/a4g/ontology#hasLegalName> ?name .
}"""
TEST_QUERY_UNIQUE_CET_ROOTS = """
SELECT distinct ?s
WHERE { ?s a <http://www.w3.org/ns/org#Organization> .
?s <http://www.meaningfy.ws/mdr#isCanonicalEntity> True .
}
"""


def test_deduplicate_entities_by_cet_uri(notice_with_rdf_manifestation, organisation_cet_uri):
    fuseki_triple_store = FusekiAdapter()
    if TEST_MDR_REPOSITORY not in fuseki_triple_store.list_repositories():
        fuseki_triple_store.create_repository(repository_name=TEST_MDR_REPOSITORY)
    notice_with_rdf_manifestation.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=notice_with_rdf_manifestation.rdf_manifestation.copy())
    deduplicate_entities_by_cet_uri(notices=[notice_with_rdf_manifestation], cet_uri=organisation_cet_uri,
                                    mdr_dataset_name=TEST_MDR_REPOSITORY)

    sparql_endpoint = fuseki_triple_store.get_sparql_triple_store_endpoint(repository_name=TEST_MDR_REPOSITORY)
    unique_names = sparql_endpoint.with_query(sparql_query=TEST_QUERY_UNIQUE_NAMES).fetch_tabular()
    unique_cet_roots = sparql_endpoint.with_query(sparql_query=TEST_QUERY_UNIQUE_CET_ROOTS).fetch_tabular()

    fuseki_triple_store.delete_repository(repository_name=TEST_MDR_REPOSITORY)

    assert len(unique_names) == len(unique_cet_roots)
