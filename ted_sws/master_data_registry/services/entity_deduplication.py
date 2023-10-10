import pathlib
import tempfile
from collections import defaultdict
from io import StringIO
from typing import List, Tuple, Dict

import rdflib
from pymongo import MongoClient
from rdflib import RDF, URIRef, OWL

from ted_sws.alignment_oracle.services.generate_alignment_links import generate_alignment_links, TURTLE_SOURCE_DATA_TYPE
from ted_sws.alignment_oracle.services.limes_config_resolver import get_limes_config_generator_by_cet_uri
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLStringEndpoint
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter, TripleStoreABC, \
    FUSEKI_REPOSITORY_ALREADY_EXIST_ERROR_MSG
from ted_sws.event_manager.services.log import log_error, log_notice_error
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_rdf_fragments_by_cet_uri_from_notices, \
    merge_rdf_fragments_into_graph, write_rdf_fragments_in_triple_store, RDF_FRAGMENT_FROM_NOTICE_PROPERTY, \
    get_procedure_subjects, get_rdf_fragment_by_root_uri_from_notice

MDR_TEMPORARY_FUSEKI_DATASET_NAME = "tmp_mdr_dataset"
MDR_FUSEKI_DATASET_NAME = "mdr_dataset"
MDR_CANONICAL_CET_PROPERTY = rdflib.term.URIRef("http://www.meaningfy.ws/mdr#isCanonicalEntity")
DEDUPLICATE_PROCEDURE_ENTITIES_DOMAIN_ACTION = "deduplicate_procedure_entities"


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


def reduce_link_set(alignment_graph: rdflib.Graph, source_subjects: set, canonical_cets: set) -> rdflib.Graph:
    """
        This function reduce number of alignment links from alignment graph.
    :param alignment_graph:
    :param source_subjects:
    :param canonical_cets:
    :return:
    """

    def copy_rdf_graph(graph: rdflib.Graph) -> rdflib.Graph:
        copy_graph = rdflib.Graph()
        for graph_triple in iter(graph):
            copy_graph.add(graph_triple)
        return copy_graph

    reduced_graph = copy_rdf_graph(graph=alignment_graph)
    found_transition = True
    while found_transition:
        found_transition = False
        for canonical_cet in canonical_cets:
            for triple in alignment_graph.triples(triple=(None, OWL.sameAs, canonical_cet)):
                if (triple[0] != triple[2]) and (triple[0] in source_subjects):
                    for transition_triple in alignment_graph.triples(triple=(None, OWL.sameAs, triple[0])):
                        found_transition = True
                        reduced_graph.remove(triple=transition_triple)
                        if triple[2] != transition_triple[0]:
                            reduced_graph.add(triple=(transition_triple[0], transition_triple[1], triple[2]))
                else:
                    reduced_graph.remove(triple=triple)
        if found_transition:
            alignment_graph = copy_rdf_graph(graph=reduced_graph)
            canonical_cets = [canonical_cet for canonical_cet in canonical_cets
                              if next(alignment_graph.triples(triple=(None, OWL.sameAs, canonical_cet)), None)]
    return reduced_graph


def filter_new_canonical_entities(cet_rdf_fragments: List[rdflib.Graph], cet_uri: str,
                                  alignment_graph: rdflib.Graph) -> Tuple[Dict, Dict]:
    """
        This function filter new canonical CETs fragments by simple CETs fragments.
    :param cet_rdf_fragments:
    :param cet_uri:
    :param alignment_graph:
    :return:
    """
    new_canonical_entities = dict()
    non_canonical_entities = dict()

    cet_rdf_fragments_dict = {
        next(cet_rdf_fragment.triples(triple=(None, RDF.type, URIRef(cet_uri))))[0]: cet_rdf_fragment
        for cet_rdf_fragment in cet_rdf_fragments}
    source_subjects = set(cet_rdf_fragments_dict.keys())

    for subject in source_subjects:
        if next(alignment_graph.triples(triple=(subject, OWL.sameAs, None)), None) is not None:
            non_canonical_entities[subject] = cet_rdf_fragments_dict[subject]
        else:
            new_canonical_entities[subject] = cet_rdf_fragments_dict[subject]

    return new_canonical_entities, non_canonical_entities


def register_new_cets_in_mdr(new_canonical_entities: Dict[rdflib.URIRef, rdflib.Graph], triple_store: TripleStoreABC,
                             mdr_dataset_name: str):
    """
        This function register new canonical CETs in MDR.
    :param new_canonical_entities:
    :param triple_store:
    :param mdr_dataset_name:
    :return:
    """
    for root_uri, cet_rdf_fragment in new_canonical_entities.items():
        cet_rdf_fragment.add(triple=(rdflib.term.URIRef(root_uri),
                                     MDR_CANONICAL_CET_PROPERTY,
                                     rdflib.term.Literal(True)))
    write_rdf_fragments_in_triple_store(rdf_fragments=list(new_canonical_entities.values()), triple_store=triple_store,
                                        repository_name=mdr_dataset_name)


def inject_similarity_links_in_notices(notices: List[Notice],
                                       cet_rdf_fragments_dict: Dict[rdflib.URIRef, rdflib.Graph],
                                       alignment_graph: rdflib.Graph, inject_reflexive_links: bool = False):
    """
        This function inject similarity links in Notice distilled rdf manifestation.
    :param notices:
    :param cet_rdf_fragments_dict:
    :param alignment_graph:
    :param inject_reflexive_links:
    :return:
    """
    notices_dict = {notice.ted_id: notice for notice in notices}

    for root_uri, cet_rdf_fragment in cet_rdf_fragments_dict.items():
        notice_id = str(next(cet_rdf_fragment.triples(triple=(root_uri, RDF_FRAGMENT_FROM_NOTICE_PROPERTY, None)))[2])
        notice = notices_dict[notice_id]
        inject_links = rdflib.Graph()
        if inject_reflexive_links:
            inject_links.add((root_uri, OWL.sameAs, root_uri))
        else:
            for triple in alignment_graph.triples(triple=(root_uri, OWL.sameAs, None)):
                inject_links.add(triple)
        notice.distilled_rdf_manifestation.object_data = '\n'.join([notice.distilled_rdf_manifestation.object_data,
                                                                    str(inject_links.serialize(format="nt"))])


def create_mdr_alignment_links(cet_rdf_fragments: List[rdflib.Graph], cet_uri: str,
                               mdr_sparql_endpoint: str) -> rdflib.Graph:
    """
        This function create alignment links for input with MDR for concrete CET URI.
    :param cet_rdf_fragments:
    :param cet_uri:
    :param mdr_sparql_endpoint:
    :return:
    """
    merged_rdf_fragments = merge_rdf_fragments_into_graph(rdf_fragments=cet_rdf_fragments)
    local_alignment_graph = generate_mdr_alignment_links(merged_rdf_fragments=merged_rdf_fragments, cet_uri=cet_uri)
    mdr_alignment_graph = generate_mdr_alignment_links(merged_rdf_fragments=merged_rdf_fragments, cet_uri=cet_uri,
                                                       mdr_sparql_endpoint=mdr_sparql_endpoint)
    canonical_cets = {triple[2] for triple in iter(mdr_alignment_graph)}
    alignment_graph = local_alignment_graph + mdr_alignment_graph

    source_subjects = {next(cet_rdf_fragment.triples(triple=(None, RDF.type, URIRef(cet_uri))))[0]
                       for cet_rdf_fragment in cet_rdf_fragments}
    if not canonical_cets:
        canonical_cets = source_subjects
    else:
        source_subjects.difference_update(canonical_cets)
    reduced_link_set = reduce_link_set(alignment_graph=alignment_graph, source_subjects=source_subjects,
                                       canonical_cets=canonical_cets)

    return reduced_link_set


def deduplicate_entities_by_cet_uri(notices: List[Notice], cet_uri: str,
                                    mdr_dataset_name: str = MDR_FUSEKI_DATASET_NAME):
    """
        This function deduplicate entities by specific CET for each notice from batch of notices.
    :param notices:
    :param cet_uri:
    :param mdr_dataset_name:
    :return:
    """
    triple_store = FusekiAdapter()
    if mdr_dataset_name not in triple_store.list_repositories():
        try:
            triple_store.create_repository(repository_name=mdr_dataset_name)
        except Exception as exception:
            if str(exception) != FUSEKI_REPOSITORY_ALREADY_EXIST_ERROR_MSG:
                log_error(message=str(exception))

    mdr_sparql_endpoint = triple_store.get_sparql_triple_store_endpoint_url(repository_name=mdr_dataset_name)
    cet_rdf_fragments = get_rdf_fragments_by_cet_uri_from_notices(notices=notices, cet_uri=cet_uri)

    cet_alignment_links = create_mdr_alignment_links(cet_rdf_fragments=cet_rdf_fragments, cet_uri=cet_uri,
                                                     mdr_sparql_endpoint=mdr_sparql_endpoint)

    new_canonical_cet_fragments_dict, non_canonical_cet_fragments_dict = filter_new_canonical_entities(
        cet_rdf_fragments=cet_rdf_fragments,
        cet_uri=cet_uri,
        alignment_graph=cet_alignment_links
    )

    register_new_cets_in_mdr(new_canonical_entities=new_canonical_cet_fragments_dict, triple_store=triple_store,
                             mdr_dataset_name=mdr_dataset_name)

    inject_similarity_links_in_notices(notices=notices, cet_rdf_fragments_dict=non_canonical_cet_fragments_dict,
                                       alignment_graph=cet_alignment_links)
    inject_similarity_links_in_notices(notices=notices, cet_rdf_fragments_dict=new_canonical_cet_fragments_dict,
                                       alignment_graph=cet_alignment_links, inject_reflexive_links=True)


def deduplicate_procedure_entities(notices: List[Notice], procedure_cet_uri: str, mongodb_client: MongoClient,
                                   mdr_dataset_name: str = MDR_FUSEKI_DATASET_NAME):
    """
         This function deduplicate procedure entities for each notice from batch of notices.
    :param notices:
    :param procedure_cet_uri:
    :param mongodb_client:
    :param mdr_dataset_name:
    :return:
    """
    notice_families = defaultdict(list)
    for notice in notices:
        if notice.original_metadata and notice.original_metadata.RN:
            parent_notice_id = str(notice.original_metadata.RN[0])
            parent_notice_id = f"{parent_notice_id[4:]}-{parent_notice_id[:4]}"
            notice_families[parent_notice_id].append(notice)

    parent_uries = {}
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    triple_store = FusekiAdapter()
    if mdr_dataset_name not in triple_store.list_repositories():
        try:
            triple_store.create_repository(repository_name=mdr_dataset_name)
        except Exception as exception:
            if str(exception) != FUSEKI_REPOSITORY_ALREADY_EXIST_ERROR_MSG:
                log_error(message=str(exception))

    for parent_notice_id in notice_families.keys():
        parent_notice = notice_repository.get(reference=parent_notice_id)
        if parent_notice and parent_notice.rdf_manifestation and parent_notice.rdf_manifestation.object_data:
            rdf_content = parent_notice.rdf_manifestation.object_data
            sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content)
            result_uris = get_procedure_subjects(sparql_endpoint=sparql_endpoint)
            result_uris_len = len(result_uris)
            if result_uris_len != 1:
                notice_normalised_metadata = parent_notice.normalised_metadata
                log_notice_error(
                    message=f"Parent notice with notice_id=[{parent_notice.ted_id}] have {result_uris_len} Procedure CETs!",
                    notice_id=parent_notice.ted_id, domain_action=DEDUPLICATE_PROCEDURE_ENTITIES_DOMAIN_ACTION,
                    notice_form_number=notice_normalised_metadata.form_number if notice_normalised_metadata else None,
                    notice_status=parent_notice.status,
                    notice_eforms_subtype=notice_normalised_metadata.eforms_subtype if notice_normalised_metadata else None)
            else:
                result_uri = result_uris[0]
                parent_procedure_uri = rdflib.URIRef(result_uris[0])
                parent_uries[parent_notice_id] = parent_procedure_uri
                parent_procedure_rdf_fragment = get_rdf_fragment_by_root_uri_from_notice(notice=parent_notice,
                                                                                         root_uri=result_uri)
                parent_new_cet = {parent_procedure_uri: parent_procedure_rdf_fragment}
                register_new_cets_in_mdr(new_canonical_entities=parent_new_cet, triple_store=triple_store,
                                         mdr_dataset_name=mdr_dataset_name)

    for parent_uri_key in parent_uries.keys():
        parent_uri = parent_uries[parent_uri_key]
        for child_notice in notice_families[parent_uri_key]:
            rdf_content = child_notice.rdf_manifestation.object_data
            sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content)
            result_uris = get_procedure_subjects(sparql_endpoint=sparql_endpoint)
            result_uris_len = len(result_uris)
            if result_uris_len != 1:
                notice_normalised_metadata = child_notice.normalised_metadata
                log_notice_error(
                    message=f"Child notice with notice_id=[{child_notice.ted_id}] have {result_uris_len} Procedure CETs!",
                    notice_id=child_notice.ted_id, domain_action=DEDUPLICATE_PROCEDURE_ENTITIES_DOMAIN_ACTION,
                    notice_form_number=notice_normalised_metadata.form_number if notice_normalised_metadata else None,
                    notice_status=child_notice.status,
                    notice_eforms_subtype=notice_normalised_metadata.eforms_subtype if notice_normalised_metadata else None)
            else:
                child_procedure_uri = rdflib.URIRef(result_uris[0])
                inject_links = rdflib.Graph()
                inject_links.add((child_procedure_uri, OWL.sameAs, parent_uri))
                child_notice.distilled_rdf_manifestation.object_data = '\n'.join(
                    [child_notice.distilled_rdf_manifestation.object_data,
                     str(inject_links.serialize(format="nt"))])
