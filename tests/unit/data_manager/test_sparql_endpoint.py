from string import Template

import pandas as pd
import pytest
import rdflib

from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLStringEndpoint, TripleStoreEndpointABC, \
    SPARQLFileEndpoint
from ted_sws.master_data_registry.resources import TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH, \
    RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH

RESULTS_DICT_KEY = "results"
BINDINGS_DICT_KEY = "bindings"


def sparql_endpoint_test_helper(sparql_endpoint: TripleStoreEndpointABC, uri: str):
    sparql_query = TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query).substitute(uri=uri)
    query_table_result = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_tabular()
    assert query_table_result is not None
    assert type(query_table_result) == pd.DataFrame
    assert len(query_table_result) == 51
    query_dict_result = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_tree()
    assert query_dict_result is not None
    assert type(query_dict_result) == dict
    assert RESULTS_DICT_KEY in query_dict_result.keys()
    assert BINDINGS_DICT_KEY in query_dict_result[RESULTS_DICT_KEY].keys()
    assert len(query_dict_result[RESULTS_DICT_KEY][BINDINGS_DICT_KEY]) == 51
    with pytest.raises(Exception) as exc_info:
        sparql_endpoint.with_query(sparql_query=sparql_query).fetch_rdf()
    assert str(exc_info.value) == "Fetch RDF method work only with CONSTRUCT and DESCRIBE sparql queries!"
    sparql_query = RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    sparql_query = Template(sparql_query).substitute(uri=uri)
    query_rdf_result = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_rdf()
    assert query_rdf_result is not None
    assert type(query_rdf_result) == rdflib.Graph

def test_sparql_file_endpoint(rdf_file_path, organisation_cet_uri):
    sparql_endpoint = SPARQLFileEndpoint(rdf_file_path=rdf_file_path)
    sparql_endpoint_test_helper(sparql_endpoint=sparql_endpoint, uri=organisation_cet_uri)


def test_sparql_string_endpoint(rdf_content, organisation_cet_uri):
    sparql_endpoint = SPARQLStringEndpoint(rdf_content=rdf_content)
    sparql_endpoint_test_helper(sparql_endpoint=sparql_endpoint, uri=organisation_cet_uri)
