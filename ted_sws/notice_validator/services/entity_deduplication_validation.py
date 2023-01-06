import rdflib
from rdflib import OWL

from ted_sws.core.model.manifestation import RDFManifestation, EntityDeduplicationReport
from ted_sws.data_manager.adapters.sparql_endpoint import DEFAULT_RDF_FILE_FORMAT


def generate_rdf_manifestation_entity_deduplication_report(rdf_manifestation: RDFManifestation):
    """
        This function generate entity deduplication report for an RDF manifestation.
    :param rdf_manifestation:
    :return:
    """
    rdf_content = rdflib.Graph()
    rdf_content.parse(rdf_manifestation.object_data.encode(encoding="utf-8"), format=DEFAULT_RDF_FILE_FORMAT)
    duplicate_entities = set()
    new_entities = set()
    for triple_sub, triple_pred, triple_obj in rdf_content.triples(triple=(None, OWL.sameAs, None)):
        if triple_sub == triple_obj:
            new_entities.add(str(triple_sub))
        else:
            duplicate_entities.add(str(triple_sub))

    rdf_manifestation.deduplication_report = EntityDeduplicationReport(number_of_duplicates=len(duplicate_entities),
                                                                       number_of_cets=len(new_entities),
                                                                       uries=list(
                                                                           duplicate_entities.union(new_entities))
                                                                       )
