from rdflib import RDF, URIRef

from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_entities_by_cet_uri


def test_deduplicate_entities_by_cet_uri(notice_with_rdf_manifestation, organisation_cet_uri):
    alignment_graph = deduplicate_entities_by_cet_uri(notices=[notice_with_rdf_manifestation],
                                                      cet_uri=organisation_cet_uri)


    print(alignment_graph.serialize(format="nt"))