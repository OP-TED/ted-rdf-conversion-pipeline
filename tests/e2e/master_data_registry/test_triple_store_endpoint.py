from string import Template

import rdflib

from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint
from ted_sws.master_data_registry.resources import TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH, \
    RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH


def test_triple_store_endpoint_fetch_rdf(triple_store_endpoint_url, organisation_cet_uri):
    query = Template(TRIPLES_BY_CET_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8"))
    triple_store = SPARQLTripleStoreEndpoint(endpoint_url=triple_store_endpoint_url)
    triple_store.with_query(sparql_query=query.substitute(uri=organisation_cet_uri))
    org_uris = triple_store.fetch_tabular()
    rdf_fragment_query = Template(RDF_FRAGMENT_BY_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8"))
    for org_uri in org_uris["s"].tolist()[:2]:
        triple_store.with_query(sparql_query=rdf_fragment_query.substitute(uri=org_uri))
        rdf_result = triple_store.fetch_rdf()
        assert isinstance(rdf_result, rdflib.Graph)
