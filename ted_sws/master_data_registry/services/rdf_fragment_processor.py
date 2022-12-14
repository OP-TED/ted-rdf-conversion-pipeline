#!/usr/bin/python3

# rdf_fragment_processor.py
# Date:  29.07.2022
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

"""

"""
import pathlib
from string import Template
from typing import List, Tuple, Optional

import rdflib

from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLStringEndpoint
from ted_sws.data_manager.adapters.triple_store import TripleStoreABC
from ted_sws.master_data_registry.resources import RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH, \
    TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH, PROCEDURE_SUBJECTS_SPARQL_QUERY_TEMPLATE_PATH

RDFTriple = Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]

DEFAULT_RDF_FILE_FORMAT = "n3"
RDF_FRAGMENT_FROM_NOTICE_PROPERTY = rdflib.URIRef("http://www.meaningfy.ws/mdr#fromNotice")


def get_subjects_by_cet_uri(sparql_endpoint: SPARQLStringEndpoint, cet_uri: str) -> List[str]:
    """
        This function return a list of subjects which are of concrete CET URI type.
    :param sparql_endpoint:
    :param cet_uri:
    :return:
    """
    sparql_query = TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query).substitute(uri=cet_uri)
    query_table_result = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_tabular()
    return query_table_result["s"].to_list()


def get_procedure_subjects(sparql_endpoint: SPARQLStringEndpoint) -> List[str]:
    """
        This function return a list of procedure subjects.
    :param sparql_endpoint:
    :return:
    """
    sparql_query = PROCEDURE_SUBJECTS_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    query_table_result = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_tabular()
    return query_table_result["s"].to_list()


def get_rdf_fragment_by_root_uri(sparql_endpoint: SPARQLStringEndpoint, root_uri: str,
                                 inject_triples: List[RDFTriple] = None) -> rdflib.Graph:
    """
        This function return a RDF fragment by given root URI.
    :param sparql_endpoint:
    :param root_uri:
    :param inject_triples:
    :return:
    """
    sparql_query = RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query).substitute(uri=root_uri)
    rdf_fragment = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_rdf()
    if inject_triples:
        for inject_triple in inject_triples:
            rdf_fragment.add(inject_triple)

    return rdf_fragment


def get_rdf_fragment_by_cet_uri_from_string(rdf_content: str, cet_uri: str,
                                            rdf_content_format: str = DEFAULT_RDF_FILE_FORMAT
                                            ) -> List[rdflib.Graph]:
    """
        This function extracts from an RDF content a list of RDFFragments dependent on a CET URI.
    :param rdf_content:
    :param cet_uri:
    :param rdf_content_format:
    :return:
    """
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content, rdf_content_format=rdf_content_format)
    root_uris = get_subjects_by_cet_uri(sparql_endpoint=sparql_endpoint, cet_uri=cet_uri)
    rdf_fragments = []
    for root_uri in root_uris:
        rdf_fragment = get_rdf_fragment_by_root_uri(sparql_endpoint=sparql_endpoint, root_uri=root_uri)
        rdf_fragments.append(rdf_fragment)
    return rdf_fragments


def get_rdf_fragments_by_cet_uri_from_file(rdf_file_path: pathlib.Path, cet_uri: str,
                                           rdf_file_content_format: str = DEFAULT_RDF_FILE_FORMAT
                                           ) -> List[rdflib.Graph]:
    """
        This function extracts from an RDF file a list of RDFFragments dependent on a CET URI.
    :param rdf_file_path:
    :param cet_uri:
    :param rdf_file_content_format:
    :return:
    """
    return get_rdf_fragment_by_cet_uri_from_string(rdf_content=rdf_file_path.read_text(encoding="utf-8"),
                                                   cet_uri=cet_uri,
                                                   rdf_content_format=rdf_file_content_format)


def get_rdf_fragment_by_root_uri_from_notice(notice: Notice, root_uri: str) -> Optional[rdflib.Graph]:
    """
         This function extracts from a Notice RDF content a RDFFragment dependent on a root URI.
    :param notice:
    :param root_uri:
    :return:
    """
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=notice.rdf_manifestation.object_data,
                                          rdf_content_format=DEFAULT_RDF_FILE_FORMAT)
    rdf_fragment = get_rdf_fragment_by_root_uri(sparql_endpoint=sparql_endpoint, root_uri=root_uri,
                                                inject_triples=[(rdflib.URIRef(root_uri),
                                                                 RDF_FRAGMENT_FROM_NOTICE_PROPERTY,
                                                                 rdflib.Literal(notice.ted_id))
                                                                ]
                                                )
    return rdf_fragment



def get_rdf_fragment_by_cet_uri_from_notice(notice: Notice, cet_uri: str) -> List[rdflib.Graph]:
    """
        This function extracts from a Notice RDF content a list of RDFFragments dependent on a CET URI.
    :param notice:
    :param cet_uri:
    :return:
    """
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=notice.rdf_manifestation.object_data,
                                           rdf_content_format=DEFAULT_RDF_FILE_FORMAT)
    root_uris = get_subjects_by_cet_uri(sparql_endpoint=sparql_endpoint, cet_uri=cet_uri)
    rdf_fragments = []
    for root_uri in root_uris:
        rdf_fragment = get_rdf_fragment_by_root_uri(sparql_endpoint=sparql_endpoint, root_uri=root_uri,
                                                    inject_triples=[(rdflib.URIRef(root_uri),
                                                                     RDF_FRAGMENT_FROM_NOTICE_PROPERTY,
                                                                     rdflib.Literal(notice.ted_id))
                                                                    ]
                                                    )
        rdf_fragments.append(rdf_fragment)
    return rdf_fragments


def get_rdf_fragments_by_cet_uri_from_notices(notices: List[Notice], cet_uri: str) -> List[rdflib.Graph]:
    """
        This function foreach Notice extracts from a Notice RDF content a list of RDFFragments dependent on a CET URI.
    :param notices:
    :param cet_uri:
    :return:
    """
    rdf_fragments = []
    for notice in notices:
        rdf_fragments.extend(get_rdf_fragment_by_cet_uri_from_notice(notice=notice, cet_uri=cet_uri))
    return rdf_fragments


def merge_rdf_fragments_into_graph(rdf_fragments: List[rdflib.Graph]) -> rdflib.Graph:
    """
        This function merge rdf fragments into single graph.
    :param rdf_fragments:
    :return:
    """
    merged_graph = rdflib.Graph()
    for rdf_fragment in rdf_fragments:
        merged_graph += rdf_fragment
    return merged_graph


def write_rdf_fragments_in_file(rdf_fragments: List[rdflib.Graph], file_path: pathlib.Path):
    """
        This function write rdf fragments in file.
    :param rdf_fragments:
    :param file_path:
    :return:
    """
    merged_graph = merge_rdf_fragments_into_graph(rdf_fragments=rdf_fragments)
    with open(file_path, "w") as file:
        file.write(str(merged_graph.serialize(format="nt")))


def write_rdf_fragments_in_triple_store(rdf_fragments: List[rdflib.Graph], triple_store: TripleStoreABC,
                                        repository_name: str):
    """
        This function write rdf fragments in triple store.
    :param rdf_fragments:
    :param triple_store:
    :param repository_name:
    :return:
    """
    merged_graph = merge_rdf_fragments_into_graph(rdf_fragments=rdf_fragments)

    triple_store.add_data_to_repository(file_content=str(merged_graph.serialize(format="nt")).encode(encoding="utf-8"),
                                        mime_type="text/n3",
                                        repository_name=repository_name)
