from typing import Tuple

import rdflib
from rdflib import OWL

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLStringEndpoint
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db
from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_entities_by_cet_uri, \
    deduplicate_procedure_entities
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_subjects_by_cet_uri
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from ted_sws.notice_metadata_processor.services.notice_eligibility import notice_eligibility_checker
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper
from ted_sws.notice_transformer.services.notice_transformer import transform_notice

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
CHILD_NOTICE_ID = "003544-2021"
PARENT_NOTICE_ID = "445564-2020"


def test_deduplicate_entities_by_cet_uri(notice_with_rdf_manifestation, organisation_cet_uri):
    fuseki_triple_store = FusekiAdapter()
    if TEST_MDR_REPOSITORY in fuseki_triple_store.list_repositories():
        fuseki_triple_store.delete_repository(repository_name=TEST_MDR_REPOSITORY)
    fuseki_triple_store.create_repository(repository_name=TEST_MDR_REPOSITORY)
    notice_with_rdf_manifestation.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=notice_with_rdf_manifestation.rdf_manifestation.copy())
    deduplicate_entities_by_cet_uri(notices=[notice_with_rdf_manifestation], cet_uri=organisation_cet_uri,
                                    mdr_dataset_name=TEST_MDR_REPOSITORY)

    sparql_endpoint = fuseki_triple_store.get_sparql_triple_store_endpoint(repository_name=TEST_MDR_REPOSITORY)
    unique_names = sparql_endpoint.with_query(sparql_query=TEST_QUERY_UNIQUE_NAMES).fetch_tabular()
    unique_cet_roots = sparql_endpoint.with_query(sparql_query=TEST_QUERY_UNIQUE_CET_ROOTS).fetch_tabular()
    assert len(unique_names) == len(unique_cet_roots)

    notice_rdf_content = notice_with_rdf_manifestation.distilled_rdf_manifestation.object_data
    notice_rdf_graph = rdflib.Graph()
    notice_rdf_graph.parse(data=notice_rdf_content, format="ttl")

    non_canonical_same_as_triples = [triple for triple in notice_rdf_graph.triples(triple=(None, OWL.sameAs, None))]
    canonical_cets_set = set(unique_cet_roots["s"].tolist())
    for triple in non_canonical_same_as_triples:
        assert str(triple[2]) in canonical_cets_set

    canonical_cets_same_as_triples = []
    for canonical_cet in canonical_cets_set:
        for triple in notice_rdf_graph.triples(triple=(rdflib.URIRef(canonical_cet), OWL.sameAs, None)):
            canonical_cets_same_as_triples.append(triple)

    for triple in canonical_cets_same_as_triples:
        assert str(triple[2]) in canonical_cets_set

    fuseki_triple_store.delete_repository(repository_name=TEST_MDR_REPOSITORY)


def execute_transform_pipeline(notice_id: str, mongodb_client, procedure_cet_uri) -> Tuple[rdflib.URIRef, Notice]:
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_fetcher = NoticeFetcher(notice_repository=notice_repository,
                                   ted_api_adapter=TedAPIAdapter(
                                       request_api=TedRequestAPI()))

    notice_fetcher.fetch_notice_by_id(notice_id)
    notice = notice_repository.get(reference=notice_id)
    indexed_notice = index_notice(notice=notice)
    normalised_notice = normalise_notice(notice=indexed_notice)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    result = notice_eligibility_checker(notice=normalised_notice, mapping_suite_repository=mapping_suite_repository)
    assert result is not None
    notice_id, mapping_suite_id = result
    normalised_notice.update_status_to(new_status=NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)
    mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
    rml_mapper = RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH)
    transformed_notice = transform_notice(notice=normalised_notice, mapping_suite=mapping_suite, rml_mapper=rml_mapper)
    transformed_notice.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=transformed_notice.rdf_manifestation.copy())
    notice_repository.update(notice=transformed_notice)
    rdf_content = transformed_notice.rdf_manifestation.object_data
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content)
    result_uris = get_subjects_by_cet_uri(sparql_endpoint=sparql_endpoint, cet_uri=procedure_cet_uri)
    assert len(result_uris) == 1
    parent_procedure_uri = rdflib.URIRef(result_uris[0])

    return parent_procedure_uri, transformed_notice


def test_deduplicate_procedure_entities(procedure_cet_uri, fake_mongodb_client):
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(mongodb_client=fake_mongodb_client,
                                                                            mapping_suite_package_name="package_F03")

    child_procedure_uri, child_notice = execute_transform_pipeline(notice_id=CHILD_NOTICE_ID,
                                                                   mongodb_client=fake_mongodb_client,
                                                                   procedure_cet_uri=procedure_cet_uri)
    parent_procedure_uri, parent_notice = execute_transform_pipeline(notice_id=PARENT_NOTICE_ID,
                                                                     mongodb_client=fake_mongodb_client,
                                                                     procedure_cet_uri=procedure_cet_uri)

    deduplicate_procedure_entities(notices=[child_notice], procedure_cet_uri=procedure_cet_uri,
                                   mongodb_client=fake_mongodb_client)

    notice_rdf_content = child_notice.distilled_rdf_manifestation.object_data
    notice_rdf_graph = rdflib.Graph()
    notice_rdf_graph.parse(data=notice_rdf_content, format="ttl")

    assert len(list(notice_rdf_graph.triples((child_procedure_uri, OWL.sameAs, parent_procedure_uri)))) == 1
