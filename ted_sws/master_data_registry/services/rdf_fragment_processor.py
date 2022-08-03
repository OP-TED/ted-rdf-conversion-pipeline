#!/usr/bin/python3

# rdf_fragment_processor.py
# Date:  29.07.2022
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

"""

"""
import pathlib
from string import Template
from typing import List

from rdflib import Graph

from ted_sws.master_data_registry.model.rdf_fragment import RDFFragment
from ted_sws.master_data_registry.resources import RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH, \
    TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH

DEFAULT_RDF_FILE_FORMAT = "n3"


def get_rdf_fragment_by_cet_uri_from_string(rdf_file_content: str, cet_uri: str,
                                            rdf_file_content_format: str = DEFAULT_RDF_FILE_FORMAT) -> List[
    RDFFragment]:
    """
        This function extracts from an RDF file content a list of RDFFragments dependent on a CET URI.
    :param rdf_file_content:
    :param cet_uri:
    :param rdf_file_content_format:
    :return:
    """
    rdf_graph = Graph()
    rdf_graph.parse(data=rdf_file_content, format=rdf_file_content_format)
    sparql_query = TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query)
    triples_by_cet_uri_result = rdf_graph.query(
        query_object=sparql_query.substitute(
            uri=cet_uri))
    sparql_query = RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query)
    rdf_fragments = []
    for row in triples_by_cet_uri_result:
        rdf_fragment_by_uri_result = rdf_graph.query(sparql_query.substitute(uri=str(row.s)))
        rdf_fragments.append(RDFFragment(rdf_content=rdf_file_content,
                                         sparql_query=sparql_query.substitute(uri=str(row.s)),
                                         rdf_fragment_triples=[row for row in rdf_fragment_by_uri_result]))
    return rdf_fragments


def get_rdf_fragments_by_cet_uri_from_file(rdf_file_path: pathlib.Path, cet_uri: str,
                                           rdf_file_content_format: str = DEFAULT_RDF_FILE_FORMAT) -> List[RDFFragment]:
    """
        This function extracts from an RDF file a list of RDFFragments dependent on a CET URI.
    :param rdf_file_path:
    :param cet_uri:
    :param rdf_file_content_format:
    :return:
    """
    rdf_file_content = rdf_file_path.read_text(encoding="utf-8")
    return get_rdf_fragment_by_cet_uri_from_string(rdf_file_content=rdf_file_content, cet_uri=cet_uri,
                                                   rdf_file_content_format=rdf_file_content_format)
