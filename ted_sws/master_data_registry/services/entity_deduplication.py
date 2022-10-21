import pathlib
import tempfile
from io import StringIO
from typing import List

import rdflib
from rdflib import RDF, URIRef, OWL

from ted_sws.alignment_oracle.services.generate_alignment_links import generate_alignment_links, TURTLE_SOURCE_DATA_TYPE
from ted_sws.alignment_oracle.services.limes_config_resolver import get_limes_config_generator_by_cet_uri
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_rdf_fragments_by_cet_uri_from_notices, \
    merge_rdf_fragments_into_graph

MDR_TEMPORARY_FUSEKI_DATASET_NAME = "tmp_mdr_dataset"
MDR_FUSEKI_DATASET_NAME = "https://fuseki.ted-data.eu/test_limes/query"


def init_master_data_registry() -> FusekiAdapter:
    """
        This function is used for master data registry initialisation.
    :return:
    """
    triple_store = FusekiAdapter()
    if MDR_FUSEKI_DATASET_NAME not in triple_store.list_repositories():
        triple_store.create_repository(repository_name=MDR_FUSEKI_DATASET_NAME)
    return triple_store


def generate_mdr_alignment_links(merged_rdf_fragments: rdflib.Graph, cet_uri: str) -> rdflib.Graph:
    tmp_rdf_file = tempfile.NamedTemporaryFile(suffix=".ttl")
    tmp_rdf_file.write(str(merged_rdf_fragments.serialize(format="turtle")).encode(encoding="utf-8"))
    tmp_rdf_file_path = tmp_rdf_file.name
    limes_config_generator = get_limes_config_generator_by_cet_uri(cet_uri=cet_uri)
    with tempfile.TemporaryDirectory() as tmp_result_dir_path:
        limes_config_params = limes_config_generator(source_sparql_endpoint=tmp_rdf_file_path,
                                                     target_sparql_endpoint=tmp_rdf_file_path,
                                                     result_dir_path=pathlib.Path(tmp_result_dir_path)
                                                     )
        limes_config_params.source.data_type = TURTLE_SOURCE_DATA_TYPE
        limes_config_params.target.data_type = TURTLE_SOURCE_DATA_TYPE
        alignment_links = generate_alignment_links(limes_config_params=limes_config_params, threshold=0.95)
    tmp_rdf_file.close()
    alignment_graph = rdflib.Graph()
    alignment_graph.parse(StringIO(alignment_links), format="nt")
    return alignment_graph


def clean_mdr_alignment_links(alignment_graph: rdflib.Graph) -> rdflib.Graph:
    """
        Clear redundant links from alignment graph.
    :param alignment_graph:
    :return:
    """
    for source_triple in alignment_graph.triples(triple=(None, OWL.sameAs, None)):
        if source_triple[0] != source_triple[2]:
            for target_triple in alignment_graph.triples(triple=(source_triple[2], OWL.sameAs, source_triple[0])):
                alignment_graph.remove(target_triple)
        else:
            alignment_graph.remove(triple=source_triple)

    return alignment_graph




def deduplicate_entities_by_cet_uri(notices: List[Notice], cet_uri: str) -> rdflib.Graph:
    """

    :param notices:
    :param cet_uri:
    :return:
    """
    rdf_fragments = get_rdf_fragments_by_cet_uri_from_notices(notices=notices, cet_uri=cet_uri)
    merged_rdf_fragments = merge_rdf_fragments_into_graph(rdf_fragments=rdf_fragments)
    triple_store = init_master_data_registry()
    alignment_graph = generate_mdr_alignment_links(merged_rdf_fragments=merged_rdf_fragments, cet_uri=cet_uri)
    clean_alignment_graph = clean_mdr_alignment_links(alignment_graph=alignment_graph)

    for source_triple in merged_rdf_fragments.triples(triple=(None, RDF.type, URIRef(cet_uri))):
        print("*" * 50)
        print("SOURCE:", source_triple[0].split("/")[-1])
        print(next(clean_alignment_graph.triples(triple=(source_triple[0], OWL.sameAs, None)), None))
        # for target_triple in clean_alignment_graph.triples(triple=(source_triple[0], OWL.sameAs, None)):
        #     print("TARGET:", target_triple[2].split("/")[-1])
        # print("*" * 50)
    return alignment_graph
