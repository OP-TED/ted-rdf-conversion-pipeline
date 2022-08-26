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

import rdflib
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLStringEndpoint
from ted_sws.master_data_registry.resources import RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH, \
    TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH

DEFAULT_RDF_FILE_FORMAT = "n3"


def get_rdf_fragment_by_cet_uri_from_string(rdf_content: str, cet_uri: str,
                                            rdf_content_format: str = DEFAULT_RDF_FILE_FORMAT) -> List[rdflib.Graph]:
    """
        This function extracts from an RDF file content a list of RDFFragments dependent on a CET URI.
    :param rdf_content:
    :param cet_uri:
    :param rdf_content_format:
    :return:
    """
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content, rdf_content_format=rdf_content_format)
    sparql_query = TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query).substitute(uri=cet_uri)
    query_table_result = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_tabular()
    sparql_query = RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query)
    rdf_fragments = []
    query_list_result = query_table_result["s"].to_list()
    for uri in query_list_result:
        rdf_fragment = sparql_endpoint.with_query(
            sparql_query=sparql_query.substitute(uri=uri)).fetch_rdf()
        rdf_fragments.append(rdf_fragment)
    return rdf_fragments


def get_rdf_fragments_by_cet_uri_from_file(rdf_file_path: pathlib.Path, cet_uri: str,
                                           rdf_file_content_format: str = DEFAULT_RDF_FILE_FORMAT) -> List[
    rdflib.Graph]:
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
