import pathlib
import tempfile
from io import StringIO
from string import Template
from typing import List, Set

import rdflib
from rdflib import RDF, URIRef, OWL

from ted_sws.alignment_oracle.services.generate_alignment_links import generate_alignment_links, TURTLE_SOURCE_DATA_TYPE
from ted_sws.alignment_oracle.services.limes_config_resolver import get_limes_config_generator_by_cet_uri
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.master_data_registry.resources import RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_rdf_fragments_by_cet_uri_from_notices, \
    merge_rdf_fragments_into_graph, write_rdf_fragments_in_triple_store

MDR_TEMPORARY_FUSEKI_DATASET_NAME = "tmp_mdr_dataset"
MDR_FUSEKI_DATASET_NAME = "mdr_dataset"
MDR_FUSEKI_URL = "https://fuseki.ted-data.eu/mdr_dataset/query"
MDR_CANONICAL_CET_PROPERTY = rdflib.term.URIRef("http://www.meaningfy.ws/mdr#isCanonicalEntity")


def init_master_data_registry() -> FusekiAdapter:
    """
        This function is used for master data registry initialisation.
    :return:
    """
    triple_store = FusekiAdapter()
    if MDR_FUSEKI_DATASET_NAME not in triple_store.list_repositories():
        triple_store.create_repository(repository_name=MDR_FUSEKI_DATASET_NAME)
    return triple_store


def generate_mdr_alignment_links(merged_rdf_fragments: rdflib.Graph, cet_uri: str,
                                 mdr_sparql_endpoint: str = None) -> rdflib.Graph:
    """
        This function is used for generate alignment links.
    :param merged_rdf_fragments:
    :param cet_uri:
    :param mdr_sparql_endpoint:
    :return:
    """
    tmp_rdf_file = tempfile.NamedTemporaryFile(suffix=".ttl")
    tmp_rdf_file.write(str(merged_rdf_fragments.serialize(format="turtle")).encode(encoding="utf-8"))
    tmp_rdf_file_path = tmp_rdf_file.name
    limes_config_generator = get_limes_config_generator_by_cet_uri(cet_uri=cet_uri)
    with tempfile.TemporaryDirectory() as tmp_result_dir_path:
        target_sparql_endpoint = mdr_sparql_endpoint if mdr_sparql_endpoint else tmp_rdf_file_path
        limes_config_params = limes_config_generator(source_sparql_endpoint=tmp_rdf_file_path,
                                                     target_sparql_endpoint=target_sparql_endpoint,
                                                     result_dir_path=pathlib.Path(tmp_result_dir_path)
                                                     )
        limes_config_params.source.data_type = TURTLE_SOURCE_DATA_TYPE
        if mdr_sparql_endpoint is None:
            limes_config_params.target.data_type = TURTLE_SOURCE_DATA_TYPE
        alignment_links = generate_alignment_links(limes_config_params=limes_config_params, threshold=0.95,
                                                   use_caching=False)
    tmp_rdf_file.close()
    alignment_graph = rdflib.Graph()
    alignment_graph.parse(StringIO(alignment_links), format="nt")
    return alignment_graph


def clean_mdr_alignment_links(source_subjects: Set[rdflib.term.URIRef], alignment_graph: rdflib.Graph) -> rdflib.Graph:
    """
        Clear redundant links from alignment graph.
    :param source_subjects:
    :param alignment_graph:
    :return:
    """
    for source_triple in alignment_graph.triples(triple=(None, OWL.sameAs, None)):
        rdf_subject, rdf_predicate, rdf_object = source_triple
        if (rdf_subject != rdf_object) and (rdf_subject in source_subjects):
            for target_triple in alignment_graph.triples(triple=(rdf_object, OWL.sameAs, rdf_subject)):
                alignment_graph.remove(triple=target_triple)
        else:
            alignment_graph.remove(triple=source_triple)

    return alignment_graph


def reduce_link_set(alignment_graph: rdflib.Graph, source_subjects: set) -> rdflib.Graph:
    """

    :param alignment_graph:
    :param source_subjects:
    :return:
    """
    reduced_graph = rdflib.Graph()
    found_transition = True
    while found_transition:
        found_transition = False
        alignment_graph = clean_mdr_alignment_links(source_subjects=source_subjects,
                                                  alignment_graph=alignment_graph)
        for triple in iter(alignment_graph):
            save_current_triple = True
            for transition_triple in alignment_graph.triples(triple=(triple[2], OWL.sameAs, None)):
                save_current_triple = False
                found_transition = True
                alignment_graph.add((triple[0], triple[1], transition_triple[2]))
            if save_current_triple:
                reduced_graph.add(triple)
            else:
                alignment_graph.remove(triple)
    return reduced_graph


def register_new_cet_in_mdr(root_uri: rdflib.term.URIRef, rdf_fragment: rdflib.Graph, mdr_sparql_endpoint: str):
    """

    :param root_uri:
    :param rdf_fragment:
    :param mdr_sparql_endpoint:
    :return:
    """
    # rdf_fragment.add((root_uri,))


def deduplicate_entities_by_cet_uri(notices: List[Notice], cet_uri: str,
                                    mdr_sparql_endpoint: str = MDR_FUSEKI_URL) -> rdflib.Graph:
    """

    :param notices:
    :param cet_uri:
    :return:
    """
    cet_rdf_fragments = get_rdf_fragments_by_cet_uri_from_notices(notices=notices, cet_uri=cet_uri)
    cet_rdf_fragments_dict = {
        next(cet_rdf_fragment.triples(triple=(None, RDF.type, URIRef(cet_uri))))[0]: cet_rdf_fragment
        for cet_rdf_fragment in cet_rdf_fragments}
    merged_rdf_fragments = merge_rdf_fragments_into_graph(rdf_fragments=cet_rdf_fragments)
    triple_store = init_master_data_registry()
    alignment_graph = generate_mdr_alignment_links(merged_rdf_fragments=merged_rdf_fragments, cet_uri=cet_uri)
    alignment_graph += generate_mdr_alignment_links(merged_rdf_fragments=merged_rdf_fragments, cet_uri=cet_uri,
                                                       mdr_sparql_endpoint=mdr_sparql_endpoint)
    source_subjects = set(cet_rdf_fragments_dict.keys())
    reduced_link_set = reduce_link_set(alignment_graph=alignment_graph, source_subjects=source_subjects)
    new_canonical_entities = []
    notices_dict = {}
    for subject in source_subjects:
        cet_rdf_fragment: rdflib.Graph = cet_rdf_fragments_dict[subject]
        if next(reduced_link_set.triples(triple=(subject, OWL.sameAs, None)), None) is not None:
            print("Ref CET:", subject.split("/")[-1])
            for triple in reduced_link_set.triples(triple=(subject, OWL.sameAs, None)):
                print("Triple:", triple)
        else:
            cet_rdf_fragment.add(triple=(rdflib.term.URIRef(subject),
                                         MDR_CANONICAL_CET_PROPERTY,
                                         rdflib.term.Literal(True)))
            new_canonical_entities.append(cet_rdf_fragment)

    write_rdf_fragments_in_triple_store(rdf_fragments=new_canonical_entities, triple_store=triple_store,
                                        repository_name=MDR_FUSEKI_DATASET_NAME)

    return alignment_graph
