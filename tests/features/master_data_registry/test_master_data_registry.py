"""Master Data Registry feature tests."""
import rdflib
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)
from rdflib import OWL

from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_procedure_entities, \
    deduplicate_entities_by_cet_uri


@scenario('test_master_data_registry.feature', 'Deduplicate organisation CET')
def test_deduplicate_organisation_cet():
    """Deduplicate organisation CET."""


@scenario('test_master_data_registry.feature', 'Deduplicate procedure CET')
def test_deduplicate_procedure_cet():
    """Deduplicate procedure CET."""


@given('a notice')
def a_notice(notice_with_rdf_manifestation):
    """a notice."""
    assert notice_with_rdf_manifestation


@given('knowing a MongoDB endpoint')
def knowing_a_mongodb_endpoint(fake_mongodb_client_with_parent_notice):
    """knowing a MongoDB endpoint."""
    assert fake_mongodb_client_with_parent_notice


@given('knowing the MDR dataset name')
def knowing_the_mdr_dataset_name(mdr_repository_name):
    """knowing the MDR dataset name."""
    assert mdr_repository_name
    assert type(mdr_repository_name) == str


@given('the notice status is TRANSFORMED')
def the_notice_status_is_transformed(notice_with_rdf_manifestation):
    """the notice status is TRANSFORMED."""
    assert notice_with_rdf_manifestation.status == NoticeStatus.TRANSFORMED


@when('the organisation CET deduplication is executed', target_fixture="distilled_notice")
def the_organisation_cet_deduplication_is_executed(notice_with_rdf_manifestation, organisation_cet_uri,
                                                   mdr_repository_name):
    """the organisation CET deduplication is executed."""
    fuseki_triple_store = FusekiAdapter()
    if mdr_repository_name in fuseki_triple_store.list_repositories():
        fuseki_triple_store.delete_repository(repository_name=mdr_repository_name)
    fuseki_triple_store.create_repository(repository_name=mdr_repository_name)
    notice_with_rdf_manifestation.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=notice_with_rdf_manifestation.rdf_manifestation.copy())
    deduplicate_entities_by_cet_uri(notices=[notice_with_rdf_manifestation], cet_uri=organisation_cet_uri,
                                    mdr_dataset_name=mdr_repository_name)
    return notice_with_rdf_manifestation


@when('the procedure CET deduplication is executed', target_fixture="distilled_notice")
def the_procedure_cet_deduplication_is_executed(child_notice, procedure_cet_uri, notice_procedure_uri,
                                                fake_mongodb_client_with_parent_notice):
    """the procedure CET deduplication is executed."""
    deduplicate_procedure_entities(notices=[child_notice], procedure_cet_uri=procedure_cet_uri,
                                   mongodb_client=fake_mongodb_client_with_parent_notice)
    return child_notice


@then('the MDR contain organisation canonical entities')
def the_mdr_contain_organisation_canonical_entities(mdr_repository_name, sparql_query_unique_names,
                                                    sparql_query_unique_cet_roots):
    """the MDR contain organisation canonical entities."""
    fuseki_triple_store = FusekiAdapter()
    sparql_endpoint = fuseki_triple_store.get_sparql_triple_store_endpoint(repository_name=mdr_repository_name)
    unique_names = sparql_endpoint.with_query(sparql_query=sparql_query_unique_names).fetch_tabular()
    unique_cet_roots = sparql_endpoint.with_query(sparql_query=sparql_query_unique_cet_roots).fetch_tabular()
    assert len(unique_names) == len(unique_cet_roots)
    fuseki_triple_store.delete_repository(repository_name=mdr_repository_name)


@then('the notice distilled rdf manifestation contains owl:sameAs links')
def the_notice_distilled_rdf_manifestation_contains_owl_same_as_links(distilled_notice: Notice):
    """the notice distilled rdf manifestation contains owl:sameAs links."""
    notice_rdf_content = distilled_notice.distilled_rdf_manifestation.object_data
    notice_rdf_graph = rdflib.Graph()
    notice_rdf_graph.parse(data=notice_rdf_content, format="ttl")
    assert len(list(notice_rdf_graph.triples((None, OWL.sameAs, None)))) > 0


@then('the notice status is DISTILLED')
def the_notice_status_is_distilled(distilled_notice: Notice):
    """the notice status is DISTILLED."""
    assert distilled_notice.status == NoticeStatus.DISTILLED
